from tornado import gen, ioloop
from tornado.ioloop import IOLoop
import sys
from pkg_resources import iter_entry_points
import json

@gen.coroutine
def main(plugin):
    #print("plugin:",plugin['receiver'])
    response = yield plugin['receiver']("Prufa")
    print("Results: \n%s" % json.dumps(response, sort_keys=True,
    indent=4, separators=(',', ': ')))

if __name__ == "__main__":
    if(len(sys.argv) > 1):
        iplugin = __import__("%s" % sys.argv[1])
        plugin = iplugin.plugin
        instance = IOLoop.instance()
        instance.add_callback(callback=lambda: main(plugin))
        instance.start()
    else:
        for object in iter_entry_points(group='sundaytasks.plugin', name=None):
            print object.name
            plugin = object.load()
            instance = IOLoop.instance()
            instance.add_callback(callback=lambda: main(plugin))

        instance.start()
