from tornado.stack_context import StackContext
from tornado import gen
from tornado.ioloop import IOLoop
from sundaytasks.utils import get_provider
import contextlib
import sys
import traceback
import logging

@gen.coroutine
def callback(plugin, parent, doc, provider):
    """This function handles calling the plugins and spawning new plugins
    based on the event system

    @param plugin The plugin data stucture which includes all the relevant
                  information
    @param parent The parent is the RunContext which called the callback

    @param doc The doc that is passed to the plugin

    @param provider An optional provider which gets some data for you from
                    CouchDB like tokens
    """
    logging.debug("callback: %s", str(plugin['name']))
    logging.debug("doc: %s", str(doc))
    logging.debug("provider: %s", str(provider))
    response = False
    args = {"doc": doc}
    par_ext = parent.extensions
    try:
        if provider:
            provider_res = yield get_provider(provider, par_ext, doc)
            args[provider] = provider_res
        response = yield plugin['receiver'](args)
    except Exception, e:
        logging.debug("Exception: %s", str(e))
        traceback.print_exc()
        sys.exc_clear()
    if response:
        logging.debug("callback response: %s", str(response))
        if "exit" in plugin:
            logging.debug("exit")
            try:
                receiver = par_ext["exit"][plugin['exit']]['receiver']
                exit_res = yield receiver(doc, response, plugin['namespace'],
                                          plugin['url'], plugin["database"])
            except Exception, e:
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

    """
    def __init__(self, queue, extensions, doc, start):
        self.finished = {}
        self.response = {}
        self.queue = queue
        self.extensions = extensions
        self.run(start, doc)

    @contextlib.contextmanager
    def handle_events(self):
        """This function provides the context that the plugins are running in

        """
        try:
            yield
        except Exception, e:
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
        for plugin in plugins:
            logging.debug("plugin_name: %s", str(plugin['name']))
            with StackContext(self.handle_events):
                instance = IOLoop.instance()
                if "provider" in plugin:
                    provider = plugin["provider"]
                    instance.run_sync(lambda:
                                      callback(plugin, self, doc, provider), 5)
                else:
                    instance.run_sync(lambda:
                                      callback(plugin, self, doc, False), 5)
                instance.start()
