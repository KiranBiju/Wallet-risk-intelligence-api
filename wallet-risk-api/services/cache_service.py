cache = {}

def get_cached(wallet):
    return cache.get(wallet)

def set_cache(wallet, data):
    cache[wallet] = data