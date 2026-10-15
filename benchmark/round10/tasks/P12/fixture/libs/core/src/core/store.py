def put(key, value, ttl=None):
    return {key: (value, ttl)}
