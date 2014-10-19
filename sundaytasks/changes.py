"""@package sundaytasks.changes

This monitors the changes of CouchDB, this is a self contained part and is run
in its own process so it does not interfere with the main loop.

@author Olafur Arason <olafura@olafura.com>
"""
from tornado import gen
from tornado import httpclient
from tornado.ioloop import IOLoop
from tornado.escape import json_decode
import socket
import re
import sys
import signal
import logging

@gen.coroutine
class Changes(object):
    """The changes module that monitors CouchDB
    @param url The base url of the CouchDB instance
    @param database The name of the database to monitor

    """
    def __init__(self, url, database, view, port):
        self._url = url
        self._database = database
        self._view = view
        self._seq = 0
        self._nid = 0
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        logging.debug("Connecting to: %s",str(port))
        try:
            self.sock.connect(port)
        except socket.error, msg:
            logging.debug("Error: %s",str(msg))
            sys.exit(1) 
        self._run()

    def _run(self):
        """The main running function of the Changes module

        """
        url = self._url+"/"+self._database
        url += "/_changes?feed=eventsource&include_docs=true"
        if not self._view == "False":
            url += "&filter=_view&view=" + self._view
        req = httpclient.HTTPRequest(
            url=url,
            streaming_callback=self.handle_event,
            headers={"content-type": "text/event-stream"},
            request_timeout=0
        )
        http_client = httpclient.AsyncHTTPClient()
        try:
            http_client.fetch(req, self.async_callback)
        except Exception, e:
            logging.debug("Exception: %s",str(e))
            pass

    def handle_event(self, response):
        """Handle event gets the data from the changes feed and prints it out
        on the stdout so it can be picked up by the sundaytask.main

        @param response It gets a response from the http_client

        """
        logging.debug("handle_event: %s", str(response))
        lines = response.split("\n")
        if len(lines) > 2:
            secondline = lines[1]
            nid = int(secondline.strip().split(":")[1])
            if nid > self._nid:
                self._nid = nid
                match = re.search("data: {(?P<value>.*)}", response)
                if match:
                    value = match.group("value")
                    json_value = json_decode("{"+value+"}")
                    seq = int(json_value['seq'])
                    if seq > self._seq:
                        value = "{"+value
                        value += ", \"url\": \""+self._url
                        value += "\", \"database\": \""+self._database+"\"}"
                        self.sock.sendall(value+"\n")
                        self._seq = seq

    def async_callback(self, response):
        """Async callback is to handle events that like losing connection
        and it restarts the function again

        @param response It gets a response with the error

        """
        logging.debug("async_callback: %s", str(response))
        self._run()

def main(url, database, view, port):
    """The main running function

    """
    instance = IOLoop.instance()
    def shuttingdown(sig, frame):
        logging.info("Stopping SundayTasks Changes: %s", sig)
        instance.stop()
        sys.exit(0)
    signal.signal(signal.SIGINT, shuttingdown)
    signal.signal(signal.SIGTERM, shuttingdown)
    try:
        Changes(url, database, view, port)
        instance.start()
    except Exception, e:
        logging.debug("Exception main: %s", str(e))
        pass

#if __name__ == "__main__":
#    main()
