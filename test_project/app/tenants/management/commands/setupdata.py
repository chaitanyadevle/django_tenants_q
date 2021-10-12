from django.contrib.auth.models import User
from django.core.management import call_command
from django.utils.translation import gettext as _
from django.core.management.base import BaseCommand
from django.conf import settings
from django_tenants.utils import schema_context, get_tenant_model, get_tenant_domain_model


class Command(BaseCommand):

    help = ('Sets up test data with two schemas and a user per schema')

    def handle(self, *args, **kwargs):
        try:

            #Make Migrations Before Creating Schema
            call_command('makemigrations', 'tenants')
            call_command('migrate_schemas', '--shared')
            # call_command('migrate_schemas', '--tenant')

            tenant_class = get_tenant_model()
            print(tenant_class,"*"*40)
            domain_class = get_tenant_domain_model()

            #Check if Public Schema Alredy Exists
            if tenant_class.objects.filter(schema_name = 'public').exists():
                return (self.stdout.write(self.style.ERROR('Public schema already exists.')))

            if not settings.PUBLIC_DOMAIN:
                return (self.stdout.write(self.style.ERROR('Public Domain Variable missing in settings file.')))

            tenant_params1 = {
                'schema_name': 'public',
                'name': 'Public',
            }

            tenant_params2 = {
                'schema_name': 'testone',
                'name': 'Test One',
            }

            tenant_params3 = {
                'schema_name': 'testtwo',
                'name': 'Test Two',
            }

            domain_params1 = {
                'domain': 'testproject.localhost',
            }

            domain_params2 = {
                'domain': 'testone.testproject.localhost',
            }

            domain_params3 = {
                'domain': 'testtwo.testproject.localhost',
            }


            tenant_class.objects.get_or_create(**tenant_params1)
            tenant_class.objects.get_or_create(**tenant_params2)
            tenant_class.objects.get_or_create(**tenant_params3)

            domain_class.objects.create(**domain_params1)
            domain_class.objects.create(**domain_params2)
            domain_class.objects.create(**domain_params3)

            with schema_context('testone'):
                User.objects.get_or_create(first_name='Subject', last_name='One',
                                        username='subjectone', email='subjectone@mailinator.com')

            with schema_context('testtwo'):
                User.objects.get_or_create(first_name='Subject', last_name='Two',
                                        username='subjecttwo', email='subjecttwo@mailinator.com')

        except Exception as e:
            return (self.stderr.write(self.style.ERROR(str(e))))