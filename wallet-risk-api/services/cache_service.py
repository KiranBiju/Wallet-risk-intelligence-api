import redis
import json

r = redis.Redis(host='localhost', port=6379, decode_responses=True)


def get_cached(wallet):
    data = r.get(wallet)
    return json.loads(data) if data else None


def set_cache(wallet, data):
    r.setex(wallet, 300, json.dumps(data))  # cache 5 mins    