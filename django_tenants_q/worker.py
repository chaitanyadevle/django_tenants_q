import pydoc
import traceback
from multiprocessing import Value
from multiprocessing.process import current_process
from multiprocessing.queues import Queue

from django import core
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.apps.registry import apps

try:
    apps.check_apps_ready()
except core.exceptions.AppRegistryNotReady:
    import django

    django.setup()

from inspect import getfullargspec
from django_q.conf import Conf, error_reporter, logger, resource, setproctitle
from django_q.signals import post_spawn, pre_execute
from django_q.utils import close_old_django_connections, get_func_repr
from django_tenants.utils import schema_context

try:
    import psutil
except ImportError:
    psutil = None

try:
    import setproctitle
except ModuleNotFoundError:
    setproctitle = None


def worker(
    task_queue: Queue, result_queue: Queue, timer: Value, timeout: int = Conf.TIMEOUT
):
    """
    Takes a task from the task queue, tries to execute it and puts the result back in
    the result queue
    :param timeout: number of seconds wait for a worker to finish.
    :type task_queue: multiprocessing.Queue
    :type result_queue: multiprocessing.Queue
    :type timer: multiprocessing.Value
    """

    proc_name = current_process().name
    logger.info(
        _("%(proc_name)s ready for work at %(id)s")
        % {"proc_name": proc_name, "id": current_process().pid}
    )
    post_spawn.send(sender="django_q", proc_name=proc_name)
    if setproctitle:
        setproctitle.setproctitle(f"qcluster {proc_name} idle")
    task_count = 0
    if timeout is None:
        timeout = -1

    try:
        # Start reading the task queue

        for task in iter(task_queue.get, "STOP"):
            result = None
            timer.value = -1  # Idle
            task_count += 1
            # Get the function from the task
            logger.info(_(f'{proc_name} processing [{task["name"]}]'))
            f = task["func"]
            # Log task creation and set process name
            # Get the function from the task
            func_name = get_func_repr(f)
            task_name = task["name"]
            schema_name = task["kwargs"].get("schema_name", None)
            task_desc = _(
                "%(proc_name)s processing %(task_name)s '%(func_name)s' on %(schema_name)s"
            ) % {
                "proc_name": proc_name,
                "func_name": func_name,
                "task_name": task_name,
                "schema_name": schema_name,
            }
            if "group" in task:
                task_desc += f" [{task['group']}]"
            logger.info(task_desc)

            if setproctitle:
                proc_title = (
                    f"qcluster {proc_name} processing {task_name} '{func_name}'"
                )
                if "group" in task:
                    proc_title += f" [{task['group']}]"
                setproctitle.setproctitle(proc_title)

            # if it's not an instance try to get it from the string
            if not callable(f):
                # locate() returns None if f cannot be loaded
                f = pydoc.locate(f)
            close_old_django_connections()
            timer_value = task.pop("timeout", timeout)
            # signal execution
            pre_execute.send(sender="django_q", func=f, task=task)
            # execute the payload
            timer.value = timer_value  # Busy

            try:
                # Checking for the presence of kwargs
                args_state = getfullargspec(f)

                kwargs = task.get("kwargs", {})
                schema_name = kwargs.get("schema_name", None)
                if schema_name:
                    with schema_context(schema_name):
                        if args_state.varkw:
                            res = f(*task["args"], **task["kwargs"])
                        else:
                            res = f(*task["args"])
                        result = (res, True)
                else:
                    result = (None, False)

            except Exception as e:
                result = (f"{e} : {traceback.format_exc()}", False)
                if error_reporter:
                    error_reporter.report()
                if task.get("sync", False):
                    raise
            with timer.get_lock():
                # Process result
                task["result"] = result[0]
                task["success"] = result[1]
                task["stopped"] = timezone.now()
                result_queue.put(task)
                timer.value = -1  # Idle
                if setproctitle:
                    setproctitle.setproctitle(f"qcluster {proc_name} idle")
                # Recycle
                if task_count == Conf.RECYCLE or rss_check():
                    timer.value = -2  # Recycled
                    break
        logger.info(_("%(proc_name)s stopped doing work") % {"proc_name": proc_name})

    except Exception as e:
        logger.error(e)


def rss_check():
    if Conf.MAX_RSS:
        if resource:
            return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss >= Conf.MAX_RSS
        elif psutil:
            return psutil.Process().memory_info().rss >= Conf.MAX_RSS * 1024
    return False
