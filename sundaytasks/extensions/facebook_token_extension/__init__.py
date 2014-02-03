from tornado import gen
import couch
import logging


@gen.coroutine
def receiver(doc):
    logging.info("Using facebook_token")
    logging.debug("doc: %s", str(doc))
    username = doc["username"]
    db = couch.AsyncCouch("_users", "http://test:testcouch@localhost:5984")
    user = False
    try:
        user = yield db.get_doc("org.couchdb.user:%s" % username)
    except couch.NotFound, e:
        logging.debug("Couch exception: %s", str(e))
    if user and "facebook" in user:
        facebook = user["facebook"]
    else:
        facebook = {}
    logging.debug("facebook: %s", str(facebook))
    raise gen.Return(facebook)

EXTENSION = {"name": "FacebookToken", "receiver": receiver, "type": "provider"}
