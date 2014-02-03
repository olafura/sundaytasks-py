from tornado import gen, httpclient
from tornado.escape import json_decode
import logging

@gen.coroutine
def receiver(args):
    logging.info("Entering simple_plugin4")
    logging.debug("args: %s", str(args))
    http_client = httpclient.AsyncHTTPClient()
    response = yield http_client.fetch("http://localhost:5984/_uuids")
    logging.debug("reponse: %s", str(response))
    raise gen.Return(json_decode(response.body))

PLUGIN = {"name": "SimplePlugin4", "receiver": receiver, "sub": "simple3",
          "pub": "simple4"}
