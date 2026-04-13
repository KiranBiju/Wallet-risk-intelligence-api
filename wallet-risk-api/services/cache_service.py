import redis
import json
import logging

logger = logging.getLogger(__name__)

#Safe Redis connection
try:
    r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
    r.ping()
    REDIS_AVAILABLE = True
    logger.info("[CACHE] Redis connected")
except Exception as e:
    REDIS_AVAILABLE = False
    logger.warning(f"[CACHE] Redis unavailable: {e}")


def get_cached(key: str):
    if not REDIS_AVAILABLE:
        return None

    try:
        data = r.get(key)
        if data:
            return json.loads(data)
    except Exception as e:
        logger.error(f"[CACHE GET ERROR] {e}")

    return None


def set_cache(key: str, value: dict, ttl: int = 300):
    if not REDIS_AVAILABLE:
        return

    try:
        r.setex(key, ttl, json.dumps(value))
    except Exception as e:
        logger.error(f"[CACHE SET ERROR] {e}")