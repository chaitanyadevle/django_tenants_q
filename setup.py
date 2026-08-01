import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="django_tenants_q",
    version="1.2.1",
    author="Chaitanya Devale, Bryton Wishart",
    author_email="mast3rbow@gmail.com",
    include_package_data=True,
    description="An integration package for Django-Q2 with Django Tenants",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mast3rbow/django_tenants_q",
    license="MIT",
    packages=setuptools.find_packages(exclude=["test_project", "test-compose.yml"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Framework :: Django",
        "Framework :: Django :: 4.2",
        "Framework :: Django :: 5.2",
        "Framework :: Django :: 6.0",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=[
        "django-tenants>=3.10.0",
        "django-q2>=1.10.0",
        "croniter>=1.0.15",
    ],
)
