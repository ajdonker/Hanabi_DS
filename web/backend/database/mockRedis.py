from fnmatch import fnmatch

class MockRedisRepository:
    def __init__(self):
        self.data = {}
        self.deleted = []

    def get(self, key):
        return self.data.get(key)
    
    def set(self, key, value):
        self.data[key] = value

    def delete(self, *keys):
        self.deleted.extend(keys)
        for key in keys:
            self.data.pop(key, None)

    def scan(self, cursor=0, match=None, count=None):
        start = int(cursor)
        batch_size = count or 10
        keys = sorted(
            key for key in self.data
            if match is None or fnmatch(key, match)
        )
        end = start + batch_size
        next_cursor = 0 if end >= len(keys) else end
        return next_cursor, keys[start:end]
