from tornado import gen, httpclient
from tornado.escape import json_decode
import logging

@gen.coroutine
def receiver(args):
    logging.info("Enter simple_plugin")
    logging.debug("args: %s", str(args))
    http_client = httpclient.AsyncHTTPClient()
    response = yield http_client.fetch("http://localhost:5984/_session")
    logging.debug("reponse: %s", str(response))
    raise gen.Return(json_decode(response.body))

PLUGIN = {"name": "SimplePlugin2", "receiver": receiver, "sub": "start",
          "pub": "simple3"}
