from tornado.stack_context import StackContext
from tornado import gen
from tornado.ioloop import IOLoop
import contextlib
import sys
import traceback
import logging

@gen.coroutine
def callback(plugin, parent, doc, provider):
    logging.debug("callback: %s", str(plugin['name']))
    logging.debug("doc: %s", str(doc))
    logging.debug("provider: %s", str(provider))
    response = False
    args = {"doc": doc}
    par_ext = parent.extensions
    try:
        if provider:
            receiver = par_ext["provider"][provider]['receiver']
            provider_res = yield receiver(doc)
            logging.debug("provider response: %s", str(provider_res))
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
        outkeys = parent.queue.get_out(plugin['sub'], plugin['pub'])
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
    def __init__(self, queue, extensions, doc, start):
        self.finished = {}
        self.response = {}
        self.queue = queue
        self.extensions = extensions
        self.run(start, doc)

    @contextlib.contextmanager
    def handle_events(self):
        try:
            yield
        except Exception, e:
            logging.debug("Exception handle: %s", str(e))
            traceback.print_exc()

    def run(self, key, doc):
        logging.debug("key: %s", str(key))
        plugins = self.queue.get_in(key)
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
