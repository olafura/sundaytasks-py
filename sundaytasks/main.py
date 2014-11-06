"""@package sundaytasks.main
This module provides main function of the package.

It connects to the changes module that provides a feed for it that it then
passes on to the plugins from certain starting point.

@author Olafur Arason <olafura@olafura.com>

"""
from tornado import gen, ioloop, iostream, netutil
from tornado.ioloop import IOLoop
from tornado.stack_context import StackContext
from tornado.escape import json_decode
import socket
from functools import partial
import sys
import os
from pkg_resources import iter_entry_points as iter_ep
from sundaytasks.queue import Queue
from sundaytasks.runcontext import RunContext
from sundaytasks.utils import get_extensions, get_plugins
import contextlib
import subprocess
import traceback
import logging
import signal

class Main(object):

    def __init__(self, usocket, starting_point):
        """Used to run the plugins that are installed based on the starting point
        @param socket Unix socket you are watching
        @param starting_point The starting point of the plugins

        """
        self.queue = get_plugins()
        self.extensions = get_extensions()
        self.starting_point = starting_point
        self.instance = IOLoop.instance()
        unix_socket = netutil.bind_unix_socket(usocket)
        netutil.add_accept_handler(unix_socket, self.accept)
        def shuttingdown(sig, frame):
            logging.info("Stopping SundayTasks: %s", sig)
            self.instance.stop()
        signal.signal(signal.SIGINT, shuttingdown)
        signal.signal(signal.SIGTERM, shuttingdown)
        self.instance.start()

    def accept(self, connection, address):
        stream = iostream.IOStream(connection)
        callback = partial(self.readmessage, stream)
        stream.read_until("\n", callback)

    def readmessage(self, stream, message):
        logging.debug("Message: %s", message)
        json_response = json_decode(message)
        try:
            runcontext = RunContext(self.queue, self.extensions, json_response["doc"],
                        self.starting_point, json_response["url"], json_response["database"])
            self.instance.start()
        except Exception, e:
            logging.debug("Exception main: %s", str(e))
            traceback.print_exc()

