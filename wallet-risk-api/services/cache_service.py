import os
import redis
import json
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

try:
    r = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=0,
        decode_responses=True
    )

    r.ping()  

    REDIS_AVAILABLE = True
    logger.info(f"[CACHE] Redis connected at {REDIS_HOST}:{REDIS_PORT}")

except Exception as e:
    REDIS_AVAILABLE = False
    logger.warning(f"[CACHE] Redis unavailable: {e}")


def get_cached(key: str):
    if not REDIS_AVAILABLE:
        return None

    try:
        data = r.get(key)

        if data:
            logger.info(f"[CACHE HIT] {key}")
            return json.loads(data)

    except Exception as e:
        logger.error(f"[CACHE GET ERROR] {e}")

    return None


def set_cache(key: str, value: dict, ttl: int = 300):
    if not REDIS_AVAILABLE:
        return

    try:
        r.setex(key, ttl, json.dumps(value))
        logger.info(f"[CACHE SET] {key} (TTL={ttl}s)")

    except Exception as e:
        logger.error(f"[CACHE SET ERROR] {e}")