import setuptools

with open('README.md', 'r') as f:
    long_description = f.read()

setuptools.setup(
    name='django_tenants_q',
    version='1.0.1',
    author='Chaitanya Devale',
    author_email='chaitanyadevale11@gmail.com',
    include_package_data=True,
    description='An integration package for Django-Q with Django Tenants',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/chaitanyadevle/django-tenants-q',
    license='MIT',
    packages=setuptools.find_packages(exclude=["test_project", "test-compose.yml"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=[
        "django-tenants>=1.10.0",
        "django-q>=1.2.1",
        "croniter==0.3.36"
    ]
)
