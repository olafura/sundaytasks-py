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
    def __init__(self, url, database, view, usocket, no_doc, filter):
        self._url = url
        self._database = database
        self._view = view
        self._filter = filter
        self._seq = 0
        self._nid = 0
        self._usocket = usocket
        self._no_doc = no_doc
        self._run()

    def _run(self):
        """The main running function of the Changes module

        """
        url = self._url+"/"+self._database
        if not self._no_doc:
            url += "/_changes?feed=eventsource&include_docs=true"
        else:
            url += "/_changes?feed=eventsource"
        if not self._view == "False":
            url += "&filter=_view&view=" + self._view
        if not self._filter == "False":
            url += "&filter=" + self._filter
        req = httpclient.HTTPRequest(
            url=url,
            streaming_callback=self.handle_event,
            headers={"content-type": "text/event-stream"},
            request_timeout=0
        )
        http_client = httpclient.AsyncHTTPClient()
        try:
            http_client.fetch(req, self.async_callback)
        except Exception as e:
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
            logging.debug("nid: %s", str(nid))
            logging.debug("self._nid: %s", str(self._nid))
            if nid > self._nid:
                self._nid = nid
                match = re.search("data: {(?P<value>.*)}", response)
                if match:
                    logging.debug("match")
                    value = match.group("value")
                    json_value = json_decode("{"+value+"}")
                    seq = int(json_value['seq'])
                    logging.debug("seq: %s", str(seq))
                    logging.debug("self._seq: %s", str(self._seq))
                    if seq > self._seq:
                        logging.debug("New seq")
                        value = "{"+value
                        if self._no_doc:
                            value += ", \"doc\": {\"_id\": \""+json_value['id']+"\"}"
                        value += ", \"url\": \""+self._url
                        value += "\", \"database\": \""+self._database+"\"}"
                        logging.debug("Connecting to: %s",str(self._usocket))
                        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                        try:
                            sock.connect(self._usocket)
                        except socket.error as msg:
                            logging.debug("Error: %s",str(msg))
                            sys.exit(1)
                        logging.debug("sent value: %s", value)
                        sock.sendall(value+"\n")
                        sock.close()
                        self._seq = seq

    def async_callback(self, response):
        """Async callback is to handle events that like losing connection
        and it restarts the function again

        @param response It gets a response with the error

        """
        logging.debug("async_callback: %s", str(response))
        self._run()

def main(url, database, view, usocket, no_doc, filter):
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
        Changes(url, database, view, usocket, no_doc, filter)
        instance.start()
    except Exception as e:
        logging.debug("Exception main: %s", str(e))
        pass

#if __name__ == "__main__":
#    main()
