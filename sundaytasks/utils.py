from tornado import gen
from sundaytasks.queue import Queue
from pkg_resources import iter_entry_points as iter_ep
import logging

@gen.coroutine
def get_provider(provider, extensions, doc, url, database):
    receiver = extensions["provider"][provider]['receiver']
    provider_res = yield receiver(doc, url, database)
    logging.debug("provider response: %s", str(provider_res))
    raise gen.Return(provider_res)

def get_extensions():
    extensions = {"provider": {},"exit":{}}
    for extobject in iter_ep(group='sundaytasks.extension', name=None):
        logging.debug("Extension name: %s", str(extobject.name))
        extension = extobject.load()
        extensions[extension['type']][extobject.name] = extension
    return extensions

def get_plugins():
    queue = Queue()
    for pluginobject in iter_ep(group='sundaytasks.plugin', name=None):
        logging.debug("Plugin name: %s", str(pluginobject.name))
        plugin = pluginobject.load()
        if "sub" in plugin and "pub" in plugin:
            queue.add_sub(plugin['sub'], plugin)
            queue.add_pub(plugin['sub'], plugin['pub'], plugin['name'])
    return queue
