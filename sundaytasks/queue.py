class Queue(object):
    """The queue for the plugins both the pub and sub

    """
    def __init__(self):
        self._subqueue = {"start": []}
        self._pubqueue = {}

    def add_sub(self, sub, plugin):
        """Adds a plugin name and plugin to the sub queue

        @param sub The name of the plugin

        @param plugin The plugin data

        """
        if sub in self._subqueue:
            self._subqueue[sub].append(plugin)
        else:
            self._subqueue[sub] = [plugin]

    def get_sub(self, sub):
        """Gets the plugin/s for the sub if there are any

        @param sub The sub you need to fetch

        """
        if sub in self._subqueue:
            return self._subqueue[sub]
        else:
            return []

    def get_all_sub(self):
        """Gets all the subs in the queue

        """
        return self._subqueue

    def add_pub(self, sub, pub, plugin):
        """Add a pub given a sub so that the pubs aren't global but rather
        tied to the sub

        @param sub The sub that is associated with the pub

        @param pub The pub that you want to store

        @param plugin The plugin data

        """
        if sub in self._pubqueue:
            if pub in self._pubqueue[sub]:
                self._pubqueue[sub][pub].append(plugin)
            else:
                self._pubqueue[sub][pub] = [plugin]
        else:
            self._pubqueue[sub] = {}
            self._pubqueue[sub][pub] = [plugin]

    def get_pub(self, sub, pub):
        """Get the pub from the queue given the sub

        @param sub The sub thats associated with the pub

        @param pub The pub that you want to fetch

        """
        if sub in self._pubqueue and pub in self._pubqueue[sub]:
            return self._pubqueue[sub][pub]
        else:
            return []

    def get_all_pub(self):
        """Gets all the pubs in the queue

        """
        return self._pubqueue
