from setuptools import setup, find_packages

setup(
    name='sundaytasks',
    version='0.01',

    description='SundayTasks is pluggable architecture for CouchDB',

    author='Olafur Arason',
    author_email='olafura@olafura.com',
    packages=find_packages(),
    include_package_data=True,
    scripts=['scripts/stasks'],
)
