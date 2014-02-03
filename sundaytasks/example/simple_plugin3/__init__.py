from tornado import gen, httpclient
from tornado.escape import json_decode
import logging

@gen.coroutine
def receiver(args):
    logging.info("Entering simple_plugin3")
    logging.debug("args: %s", args)
    http_client = httpclient.AsyncHTTPClient()
    response = yield http_client.fetch("http://localhost:5984/_uuids")
    logging.debug("reponse: %s", str(response))
    raise gen.Return(json_decode(response.body))

PLUGIN = {"name": "SimplePlugin3", "receiver": receiver, "sub": "simple",
          "pub": "simple3"}
