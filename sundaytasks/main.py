"""@package sundaytasks.main
This module provides main function of the package.

It connects to the changes module that provides a feed for it that it then
passes on to the plugins from certain starting point.

@author Olafur Arason <olafura@olafura.com>

"""
from tornado import gen
from tornado.ioloop import IOLoop
from tornado.stack_context import StackContext
from tornado.escape import json_decode
import sys
import os
from pkg_resources import iter_entry_points as iter_ep
from sundaytasks.queue import Queue
from sundaytasks.runcontext import RunContext
import contextlib
import subprocess
import traceback
import logging
FORMAT = '%(asctime)s %(funcName)s %(levelname)-8s %(message)s'
LEVEL = logging.DEBUG
logging.basicConfig(format = FORMAT,
                    level = LEVEL)

def run(url, database, view, starting_point):
    """Used to run the plugins that are installed based on the starting point
    @param url Base url for the CouchDB instance your monitoring
    @param database Name of the database to monitor
    @param view View to filter by
    @param starting_point The starting point of the plugins

    """
    queue = Queue()
    for pluginobject in iter_ep(group='sundaytasks.plugin', name=None):
        logging.debug("Plugin name: %s", str(pluginobject.name))
        plugin = pluginobject.load()
        if "sub" in plugin and "pub" in plugin:
            queue.add_in(plugin['sub'], plugin)
            queue.add_out(plugin['sub'], plugin['pub'], plugin['name'])
    extensions = {"provider": {},"exit":{}}
    for extobject in iter_ep(group='sundaytasks.extension', name=None):
        logging.debug("Extension name: %s", str(extobject.name))
        extension = extobject.load()
        extensions[extension['type']][extobject.name] = extension
    allpluginsout = queue.get_all_out()
    allpluginsin = queue.get_all_in()
    logging.debug("allplugins out: %s", str(allpluginsout))
    logging.debug("allplugins in: %s", str(allpluginsin))
    logging.debug("extensions: %s", str(extensions))
    package_directory = os.path.dirname(os.path.abspath(__file__))
    changespath = os.path.join(package_directory, "changes.py")
    args = ["python", changespath, url, database]
    changes = subprocess.Popen(args,
                   stdout=subprocess.PIPE,
                   )
    for response in iter(changes.stdout.readline, ''):
        logging.debug("line")
        logging.debug("response: %s", str(response))
        json_response = json_decode(response)
        try:
            runcontext = RunContext(queue, extensions, json_response["doc"],
                        starting_point)
        except Exception, e:
            logging.debug("Exception main: %s", str(e))
            traceback.print_exc()
