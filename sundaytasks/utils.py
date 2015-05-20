from tornado import gen
from sundaytasks.queue import Queue
from pkg_resources import iter_entry_points as iter_ep
import logging
import copy

@gen.coroutine
def striped_copy(origin_dict):
    dict_copy = copy.copy(origin_dict)
    for key in dict_copy:
        value = dict_copy[key]
        if type(value) is dict:
            for key2 in value:
                value2 = value[key2]
                if type(value2) is str and len(value2) > 100:
                    value[key2] = "Too long to display"
            dict_copy[key] = value
        elif type(value) is str and len(value) > 100:
            dict_copy[key] = "Too long to display"
    raise gen.Return(dict_copy)

@gen.coroutine
def get_provider(provider, extensions, doc, url, database):
    receiver = extensions["provider"][provider]['receiver']
    provider_res = yield receiver(doc, url, database)
    provider_res_copy = yield striped_copy(provider_res)
    logging.debug("provider response: %s", str(provider_res_copy))
    raise gen.Return(provider_res)

def get_extensions():
    extensions = {"provider": {}, "exit":{}}
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
