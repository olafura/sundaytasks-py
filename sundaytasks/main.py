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
import signal

def get_extensions():
    extensions = {"provider": {},"exit":{}}
    for extobject in iter_ep(group='sundaytasks.extension', name=None):
        logging.debug("Extension name: %s", str(extobject.name))
        extension = extobject.load()
        extensions[extension['type']][extobject.name] = extension
    return extensions

def get_plugins():
    queue = Queue()
    for pluginobject in iter_ep(group='sundaytasks.plugin', name=None):
        logging.debug("Plugin name: %s", str(pluginobject.name))
        plugin = pluginobject.load()
        if "sub" in plugin and "pub" in plugin:
            queue.add_sub(plugin['sub'], plugin)
            queue.add_pub(plugin['sub'], plugin['pub'], plugin['name'])
    return queue

def run(url, database, view, starting_point):
    """Used to run the plugins that are installed based on the starting point
    @param url Base url for the CouchDB instance your monitoring
    @param database Name of the database to monitor
    @param view View to filter by
    @param starting_point The starting point of the plugins

    """
    queue = get_plugins()
    extensions = get_extensions()
    allpluginspub = queue.get_all_pub()
    allpluginssub = queue.get_all_sub()
    logging.debug("allplugins pub: %s", str(allpluginspub))
    logging.debug("allplugins sub: %s", str(allpluginssub))
    logging.debug("extensions: %s", str(extensions))
    package_directory = os.path.dirname(os.path.abspath(__file__))
    changespath = os.path.join(package_directory, "changes.py")
    args = ["python", changespath, url, database]
    changes = subprocess.Popen(args,
                   stdout=subprocess.PIPE,
                   )
    def shuttingdown(sig, frame):
        logging.info("Stopping SundayTasks: %s", sig)
        changes.kill()
    signal.signal(signal.SIGINT, shuttingdown)
    signal.signal(signal.SIGTERM, shuttingdown)
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
