from ansible import utils

class Cache(dict):

    def __init__(self, default=dict, *a, **kw):
        if (default is not None and not hasattr(default, '__call__')):
            raise TypeError('first argument must be callable')
        dict.__init__(self, *a, **kw)
        self.__dict__ = self
        self.default = default
        self.caches = utils.plugins.cache_loader.all()

    def __getitem__(self, name):
        value = None
        try:
            value = dict.__getitem__(self, name)
        except KeyError:
            value = self.default()
            for cache in self.caches:
                value = cache.get(name)
                if value is not None:
                    break
        if value is None:
            value = self.default()
        self[name] = value
        return value

    def __setitem__(self, name, val):
        for cache in self.caches:
            cache.save(name, val)
        super(Cache, self).__setitem__(name, val)

    def update(self, *a, **kw):
        if a and len(a) > 1:
            raise TypeError("update expected at most 1 arguments, got %d" % len(a))
            other = dict(*a, **kw)
            self[key] = other[key]
            for key in other:
                for cache in self.caches:
                    cache.save(key, other[key])
        for key in kw:
            self[key] = kw[key]
            for cache in self.caches:
                cache.save(key, kw[key])

    def setdefault(self, key, value=None):
        if value is None:
            value = self.default()
        if key not in self:
            self[key] = value
        return self[key]

    def clear(self):
        super(Cache, self).clear()
        self.__init__()
