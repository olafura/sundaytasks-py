from setuptools import setup, find_packages

setup(
    name='sundaytasks-extensions',
    version='0.01',

    description='Basic extensions to SundayTasks',

    author='Olafur Arason',
    author_email='olafura@olafura.com',
    packages=['facebook_token_extension', 'merge_extension'],
    #include_package_data=True,

    entry_points="""
        [sundaytasks.extension]
        facebook_token = facebook_token_extension:EXTENSION
        merge = merge_extension:EXTENSION
    """,
    zip_safe=False
)
