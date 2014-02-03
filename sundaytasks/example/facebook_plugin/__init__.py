from tornado import gen, httpclient
from tornado.escape import json_decode
from facebook import GraphAPI
import logging


@gen.coroutine
def receiver(args):
    logging.info("Entering facebook_pluging")
    logging.debug("args: %s", str(args))
    doc = args["doc"]
    facebook = args["facebook_token"]
    graph = GraphAPI(facebook["access_token"])
    response = graph.get_object("me")
    logging.debug("response: %s", str(response))
    raise gen.Return(response)

PLUGIN = {"name": "Facebook", "receiver": receiver, "sub": "start",
          "pub": "simple", "provider": "facebook_token",
          "namespace": "facebook", "exit": "merge", "database":"test",
          "url": "http://test:testcouch@localhost:5984"}
