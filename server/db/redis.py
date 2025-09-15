from redis.asyncio import Redis
import os


def get_redis() -> Redis:
    redis_url = os.getenv("REDIS_URL")
    if redis_url:
        return Redis.from_url(redis_url, decode_responses=True)
    return Redis(host="localhost", port=6379, decode_responses=True)


redis = get_redis()
