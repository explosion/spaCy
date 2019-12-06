from datetime import datetime, timedelta


class KeyStopWatch(object):
    def __init__(self, sw, key):
        self._sw = sw
        self._key = key

    def __enter__(self):
        self._sw.start(self._key)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._sw.stop(self._key)


class StopWatch(object):
    """A simple stop watch used to monitor execution times.

    EXAMPLE:
        >>> from spacy.cli.stopwatch import StopWatch
        >>> sw = StopWatch()
        >>>
        >>> # Use within a context
        >>> with sw.of('train'):
        >>>     # do expensive operation here
        >>> print("Operation 'train' took {} seconds".format(sw['train'].seconds))
        >>>
        >>> # or use with explicit start and stop
        >>> sw.start('dev')
        >>> # do another operation here
        >>> sw.stop('dev')
        >>> print("Operation 'dev' took {} seconds".format(sw['dev'].seconds))
    """

    def __init__(self):
        self._watches = {}

    def __contains__(self, key):
        return key in self._watches

    def __getitem__(self, item):
        if item in self._watches:
            return self._watches[item]
        return timedelta(seconds=0)

    def __delitem__(self, item):
        if item in self._watches:
            self._watches.__delitem__(item)

    def of(self, key):
        """Used inside a context to automatically start and stop the watch
        for the given key.

        key: A key to name the watch
        """
        return KeyStopWatch(self, key)

    def start(self, key):
        """Starts the watch for the given key

        key: A key to name the watch
        """
        self._watches[key] = datetime.now()
        return self

    def stop(self, key):
        """Stops the watch for the given key

        key: The watch name
        """
        if key in self._watches:
            self._watches[key] = datetime.now() - self._watches[key]
