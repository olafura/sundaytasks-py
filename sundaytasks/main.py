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
from sundaytasks.queue import Queue
from sundaytasks.runcontext import RunContext
#from sundaytasks.utils import get_extensions, get_plugins
import sundaytasks.utils
import contextlib
import subprocess
import traceback
import logging
import signal

class Main(object):

    def __init__(self, usocket, starting_point, allow_design):
        """Used to run the plugins that are installed based on the starting point
        @param socket Unix socket you are watching
        @param starting_point The starting point of the plugins

        """
        self.queue = sundaytasks.utils.get_plugins()
        self.extensions = sundaytasks.utils.get_extensions()
        self.starting_point = starting_point
        self.instance = IOLoop.instance()
        self._allow_design = allow_design
        unix_socket = netutil.bind_unix_socket(usocket)
        netutil.add_accept_handler(unix_socket, self.accept)

    def start(self):
        self.instance.start()

    def close(self):
        self.instance.stop()

    def reload(self):
        reload(sundaytasks.utils)
        self.queue = sundaytasks.utils.get_plugins()
        self.extensions = sundaytasks.utils.get_extensions()


    def accept(self, connection, address):
        logging.debug("accept")
        stream = iostream.IOStream(connection)
        callback = partial(self.readmessage, stream)
        stream.read_until("\n", callback)

    def readmessage(self, stream, message):
        logging.debug("Message: %s", message)
        json_response = json_decode(message)
        try:
            runcontext = RunContext(self.queue, self.extensions, json_response["doc"],
                        self.starting_point, json_response["url"], json_response["database"], self._allow_design)
            self.instance.start()
        except Exception as e:
            logging.debug("Exception main: %s", str(e))
            traceback.print_exc()

