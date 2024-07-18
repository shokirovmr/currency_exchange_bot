import redis
import os

REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', 6379)
REDIS_CLIENT = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
