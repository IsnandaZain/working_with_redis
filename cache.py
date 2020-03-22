import redis

import logging

log = logging.getLogger(__name__)

class Cache(object):

    def __init__(self, redis_class=redis.StrictRedis):
        self.prefix = "app_redis"
        self.redis = redis_class(
            host="127.0.0.1",
            port="6379"
        )

    def set(self, key: str, value, ex=None):
        """Set new cache

        Args:
            key: key name for cache
            value: value for cache
            ex: expire time on key (in seconds)
        """
        try:
            self.redis.set(self._addprefix(key), value, ex=ex)
        except redis.exceptions.ConnectionError as e:
            log.warning(e)


    def get(self, key: str, return_type=None, encoding="utf-8"):
        """Get value from cache with key

        Args:
            key: key name for cache
            return_type: type return value
            encoding: default encoding

        Returns:
            object value
        """
        try:
            value = self.redis.get(self._addprefix(key))
        except redis.exceptions.ConnectionError as e:
            log.warning(e)

        # sometimes redis value None as bytes None
        if value == b"None":
            value = None

        if value and return_type:
            # change value to int
            if return_type is int:
                value = int(value.decode(encoding))

            # decode value to str
            elif return_type is str:
                value = value.decode(encoding)

            else:
                raise ValueError("return type not supported")

        return value


    def update(self, key: str, value, ex=None):
        """Update value cache

        Args:
            key: key name for cache
            value: value for cache
            ex: expire time on key (in seconds)
        """
        try:
            self.redis.set(self._addprefix(key), value, ex=ex, xx=True)
        except redis.exceptions.ConnectionError as e:
            log.warning(e)


    def delete(self, key: str):
        """Delete cache from redis"""
        try:
            self.redis.delete(self._addprefix(key))
        except redis.exceptions.ConnectionError as e:
            log.warning(e)

    
    def incr(self, key: str, amount: int = 1) -> int:
        """Increment value

        Args:
            key: key name cache
            amount: total increment

        Returns:
            int value after decrement
        """
        try:
            self.redis.get(self._addprefix(key))
            if value and not value.isdigit():
                raise ValueError("cannot incr value non digit")

            value = self.redis.incr(self._addprefix(key), amount)
        except redis.exceptions.ConnectionError as e:
            log.warning(e)
            value = 0

        return value
        

    def decr(self, key: str, amount: int = 1) -> int:
        """Decrement value

        Args:
            key: key name cache
            amount: total decrement

        Returns:
            int value after increment
        """
        try:
            self.redis.get(self._addprefix(key))
            if value and not value.isdigit():
                raise ValueError("cannot decr value non digit")

            value = self.redis.decr(self._addprefix(key), amount)
        except redis.exceptions.ConnectionError as e:
            log.warning(e)
            value = 0

        return value

    
    def _addprefix(self, key: str):
        return self.prefix + "." + key

cache = Cache()