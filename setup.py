from setuptools import setup, find_packages

setup(
    name='sundaytasks',
    version='0.05',

    description='SundayTasks is pluggable architecture for CouchDB',

    author='Olafur Arason',
    author_email='olafura@olafura.com',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    scripts=['scripts/stasks','scripts/schanges','scripts/sundaytask_test_plugin'],
)
