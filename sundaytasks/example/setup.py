from setuptools import setup, find_packages

setup(
    name='sundaytasks-examples',
    version='0.01',

    description='Basic examples of plugins',

    author='Olafur Arason',
    author_email='olafura@olafura.com',
    packages=['simple_plugin', 'simple_plugin2', 'simple_plugin3', 'simple_plugin4', 'facebook_plugin'],
    #include_package_data=True,

    entry_points="""
        [sundaytasks.plugin]
        simple = simple_plugin:PLUGIN
        simple2 = simple_plugin2:PLUGIN
        simple3 = simple_plugin3:PLUGIN
        simple4 = simple_plugin4:PLUGIN
        plugin_facebook = facebook_plugin:PLUGIN
    """,
    zip_safe = False
)
