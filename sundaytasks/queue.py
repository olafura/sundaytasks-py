class Queue(object):
    """The queue for the plugins both the pub and sub

    """
    def __init__(self):
        self._inqueue = {"start": []}
        self._outqueue = {}

    def add_in(self, key, task):
        if key in self._inqueue:
            self._inqueue[key].append(task)
        else:
            self._inqueue[key] = [task]

    def get_in(self, key):
        if key in self._inqueue:
            return self._inqueue[key]
        else:
            return []

    def get_all_in(self):
        return self._inqueue

    def add_out(self, sub, pub, task):
        if sub in self._outqueue:
            if pub in self._outqueue[sub]:
                self._outqueue[sub][pub].append(task)
            else:
                self._outqueue[sub][pub] = [task]
        else:
            self._outqueue[sub] = {}
            self._outqueue[sub][pub] = [task]

    def get_out(self, sub, pub):
        if sub in self._outqueue and pub in self._outqueue[sub]:
            return self._outqueue[sub][pub]
        else:
            return []

    def get_all_out(self):
        return self._outqueue
