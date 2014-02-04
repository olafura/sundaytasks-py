class Queue(object):
    """The queue for the plugins both the pub and sub

    """
    def __init__(self):
        self._subqueue = {"start": []}
        self._pubqueue = {}

    def add_sub(self, sub, task):
        """Adds a plugin name and task to the sub queue

        @param sub The name of the plugin
        """
        if sub in self._subqueue:
            self._subqueue[sub].append(task)
        else:
            self._subqueue[sub] = [task]

    def get_sub(self, sub):
        if sub in self._subqueue:
            return self._subqueue[sub]
        else:
            return []

    def get_all_sub(self):
        return self._subqueue

    def add_pub(self, sub, pub, task):
        if sub in self._pubqueue:
            if pub in self._pubqueue[sub]:
                self._pubqueue[sub][pub].append(task)
            else:
                self._pubqueue[sub][pub] = [task]
        else:
            self._pubqueue[sub] = {}
            self._pubqueue[sub][pub] = [task]

    def get_pub(self, sub, pub):
        if sub in self._pubqueue and pub in self._pubqueue[sub]:
            return self._pubqueue[sub][pub]
        else:
            return []

    def get_all_pub(self):
        return self._pubqueue
