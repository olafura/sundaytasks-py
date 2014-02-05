"""@package sundaytasks.changes

This monitors the changes of CouchDB, this is a self contained part and is run
in its own process so it does not interfere with the main loop.

@author Olafur Arason <olafura@olafura.com>
"""
from tornado import gen
from tornado import httpclient
from tornado.ioloop import IOLoop
from tornado.escape import json_decode
import re
import sys
import signal

@gen.coroutine
class Changes(object):
    """The changes module that monitors CouchDB
    @param url The base url of the CouchDB instance
    @param database The name of the database to monitor

    """
    def __init__(self, url, database):
        self._url = url
        self._database = database
        self._seq = 0
        self._nid = 0
        self._run()

    def _run(self):
        """The main running function of the Changes module

        """
        url = self._url+"/"+self._database
        url += "/_changes?feed=eventsource&include_docs=true"
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
            #print("Exception:",e)
            pass
        #response = yield http_client.fetch(url+"/"+database)

    def handle_event(self, response):
        """Handle event gets the data from the changes feed and prints it out
        on the stdout so it can be picked up by the sundaytask.main

        @param response It gets a response from the http_client

        """
        #print("handle_event", response)
        lines = response.split("\n")
        if len(lines) > 2:
            secondline = lines[1]
            nid = int(secondline.strip().split(":")[1])
            #print("nid",nid)
            #print("self nid",self._nid)
            if nid > self._nid:
                self._nid = nid
                #firstline = lines[0]
                #print("firstline",firstline)
                match = re.search("data: (?P<value>.*)", response)
                if match:
                    value = match.group("value")
                    #print("value:", value)
                    json_value = json_decode(value)
                    seq = int(json_value['seq'])
                    #print("seq", seq)
                    #print("self seq", self._seq)
                    if seq > self._seq:
                        #print("handle_event", json_value)
                        #print(json_value)
                        sys.stdout.write(value+"\n")
                        sys.stdout.flush()
                        #self._callback(json_value)
                        #raise gen.Return(json_value)
                        self._seq = seq
                    #else:
                    #   print("Repeat")

    def async_callback(self, response):
        """Async callback is to handle events that like losing connection
        and it restarts the function again

        @param response It gets a response with the error

        """
        #print("async_callback",response)
        self._run()

def main():
    """The main running function

    """
    if len(sys.argv) > 1:
        arg_url = sys.argv[1]
        arg_database = sys.argv[2]
        instance = IOLoop.instance()
        def shuttingdown(sig, frame):
            logging.info("Stopping SundayTasks Changes: %s", sig)
            instance.stop()
        signal.signal(signal.SIGINT, shuttingdown)
        signal.signal(signal.SIGTERM, shuttingdown)
        try:
            Changes(arg_url, arg_database)
            instance.start()
        except Exception, e:
            #print("Exception main:", e)
            pass

if __name__ == "__main__":
    main()
