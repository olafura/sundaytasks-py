from tornado import gen
import couch
import logging


@gen.coroutine
def receiver(doc, changes, namespace, url, database):
    logging.info("Using merge_extension")
    logging.debug("merge doc: %s", str(doc))
    logging.debug("merge changes: %s", str(changes))
    logging.debug("merge namespace: %s", str(namespace))
    logging.debug("merge url: %s", str(url))
    logging.debug("merge database: %s", str(database))
    db = couch.AsyncCouch(database, url)
    doc[namespace] = changes
    response = ""
    try:
        response = yield db.save_doc(doc)
    except Exception, e:
        logging.debug("Couch exception: %s", str(e))
    raise gen.Return(response)

EXTENSION = {"name": "Merge", "receiver": receiver, "type": "exit"}
