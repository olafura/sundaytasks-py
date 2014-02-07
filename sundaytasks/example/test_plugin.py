from tornado import gen, ioloop
from tornado.ioloop import IOLoop
import sys
from pkg_resources import iter_entry_points as iter_ep
import json
import logging
import sundaytasks.main as st_main
from sundaytasks.runcontext import get_provider
import argparse
from tornado.escape import json_decode as jd
FORMAT = '%(asctime)s %(funcName)s %(levelname)-8s %(message)s'
LEVEL = logging.DEBUG
logging.basicConfig(format = FORMAT, level = LEVEL)

@gen.coroutine
def main(plugin, args):
    response = yield plugin['receiver'](args)
    logging.debug("Results: \n%s", json.dumps(response, sort_keys=True,
    indent=4, separators=(',', ': ')))

@gen.coroutine
def single(plugin, doc):
    #iplugin = __import__("%s" % sys.argv[1])
    iplugin = __import__("%s" % plugin)
    plugin = iplugin.PLUGIN
    if not doc:
        doc = {"_id": "testing", "username": "testing"}
    args = {"doc": doc}
    if "provider" in plugin:
        provider = plugin["provider"]
        provider_res = yield get_provider(provider, EXTENSIONS, doc)
        args[provider] = provider_res
    logging.debug("args: %s", str(args))
    instance.add_callback(callback=lambda: main(plugin, args))
    instance.start()

if __name__ == "__main__":
    EXTENSIONS = st_main.get_extensions()
    #logging.debug("Extensions: %s", str(EXTENSIONS))
    instance = IOLoop.instance()
    description = """Test plugin tests the plugin to see if it works
    """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-p','--plugin', help='Plugin to test',
                         default=False)
    parser.add_argument('-d','--doc', help='Document to give',
                         default=False)
    args = parser.parse_args()
    if args.plugin:
        if args.doc:
            instance.run_sync(lambda: single(args.plugin, jd(args.doc)))
        else:
            instance.run_sync(lambda: single(args.plugin, False))
    else:
        for object in iter_ep(group='sundaytasks.plugin', name=None):
            logging.debug("plugin: %s", str(object.name))
            plugin = object.load()
            instance.add_callback(callback=lambda: main(plugin))

        instance.start()
