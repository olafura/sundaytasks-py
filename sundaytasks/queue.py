class Queue(object):
    """The queue for the plugins both the pub and sub

    """
    def __init__(self):
        self._subqueue = {"start": []}
        self._pubqueue = {}

    def add_sub(self, sub, plugin):
        """Adds a plugin name and plugin to the sub queue

        @param sub The name of the plugin
        """
        if sub in self._subqueue:
            self._subqueue[sub].append(plugin)
        else:
            self._subqueue[sub] = [plugin]

    def get_sub(self, sub):
        if sub in self._subqueue:
            return self._subqueue[sub]
        else:
            return []

    def get_all_sub(self):
        return self._subqueue

    def add_pub(self, sub, pub, plugin):
        if sub in self._pubqueue:
            if pub in self._pubqueue[sub]:
                self._pubqueue[sub][pub].append(plugin)
            else:
                self._pubqueue[sub][pub] = [plugin]
        else:
            self._pubqueue[sub] = {}
            self._pubqueue[sub][pub] = [plugin]

    def get_pub(self, sub, pub):
        if sub in self._pubqueue and pub in self._pubqueue[sub]:
            return self._pubqueue[sub][pub]
        else:
            return []

    def get_all_pub(self):
        return self._pubqueue
