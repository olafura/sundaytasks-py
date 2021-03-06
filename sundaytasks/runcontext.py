from tornado.stack_context import StackContext
from tornado import gen
from tornado.ioloop import IOLoop
from sundaytasks.utils import get_provider
import contextlib
import sys
import traceback
import logging
import re

@gen.coroutine
def callback(plugin, parent, doc, provider, url, database):
    """This function handles calling the plugins and spawning new plugins
    based on the event system

    @param plugin The plugin data stucture which includes all the relevant
                  information
    @param parent The parent is the RunContext which called the callback

    @param doc The doc that is passed to the plugin

    @param provider An optional provider which gets some data for you from
                    CouchDB like tokens

    @param url The url of CouchDB instance

    @param database The database

    """
    logging.debug("callback: %s", str(plugin['name']))
    logging.debug("doc: %s", str(doc))
    logging.debug("provider: %s", str(provider))
    response = False
    par_ext = parent.extensions
    args = {"doc": doc}
    try:
        if provider:
            provider_res = yield get_provider(provider, par_ext, doc, url, database)
            args[provider] = provider_res
        response = yield plugin['receiver'](args)
    except Exception as e:
        logging.debug("Exception: %s", str(e))
        traceback.print_exc()
        sys.exc_clear()
    if response:
        logging.debug("callback response: %s", str(response))
        exit_res = ""
        if "exit" in plugin:
            logging.debug("exit")
            try:
                receiver = par_ext["exit"][plugin['exit']]['receiver']
                exit_res = yield receiver(doc, response, plugin['namespace'],
                                          url, database)
            except Exception as e:
                logging.debug("Exception: %s", str(e))
                traceback.print_exc()
                sys.exc_clear()
        parent.response[plugin['name']] = exit_res
        if plugin['sub'] in parent.finished:
            sub = parent.finished[plugin['sub']]
            if plugin['pub'] in parent.finished[plugin['sub']]:
                sub[plugin['pub']].append(plugin['name'])
            else:
                sub[plugin['pub']] = [plugin['name']]
        else:
            parent.finished[plugin['sub']] = {}
            parent.finished[plugin['sub']][plugin['pub']] = [plugin['name']]
        logging.debug("finished: %s", str(parent.finished))
        finished = True
        outkeys = parent.queue.get_pub(plugin['sub'], plugin['pub'])
        logging.debug("outkeys: %s", str(outkeys))
        logging.debug("_finished: %s",
                      str(parent.finished[plugin['sub']][plugin['pub']]))
        for i in outkeys:
            if i not in parent.finished[plugin['sub']][plugin['pub']]:
                finished = False
        logging.debug("finished: %s", str(finished))
        if finished:
            del parent.finished[plugin['sub']][plugin['pub']]
            parent.run(plugin['pub'], doc)


class RunContext(object):
    """The runcontext which provides an way of calling the plugin functions
    in way that does not interfere with the main loop

    @param queue The queue that contains the plugins to run

    @param extensions Available extensions to the plugins

    @param doc The doc that is passed to the plugins

    @param start The starting point used to decide where to begin

    @param url The url of CouchDB instance

    @param database The database

    """
    def __init__(self, queue, extensions, doc, start, url, database, allow_design):
        self.finished = {}
        self.response = {}
        self.queue = queue
        self.extensions = extensions
        self.url = url
        self.database = database
        self.allow_design = allow_design
        self.run(start, doc)

    @contextlib.contextmanager
    def handle_events(self):
        """This function provides the context that the plugins are running in

        """
        try:
            yield
        except Exception as e:
            logging.debug("Exception handle: %s", str(e))
            traceback.print_exc()

    def run(self, key, doc):
        """The main running function

        @param key The key in the queue to run next

        @param doc The document passed to the plugin

        """
        logging.debug("key: %s", str(key))
        plugins = self.queue.get_sub(key)
        logging.debug("plugins: %s", str(plugins))
        if not self.allow_design and re.match(r"^_design", doc['_id']):
            return
        for plugin in plugins:
            logging.debug("plugin_name: %s", str(plugin['name']))
            with StackContext(self.handle_events):
                instance = IOLoop.instance()
                if "provider" in plugin:
                    provider = plugin["provider"]
                    instance.run_sync(lambda:
                                      callback(plugin, self, doc, provider, self.url, self.database), 30)
                else:
                    instance.run_sync(lambda:
                                      callback(plugin, self, doc, False, self.url, self.database), 30)
                instance.start()
