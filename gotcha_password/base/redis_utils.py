"""
Utility functions for Redis
"""

import redis, os
from rq import Worker, Queue, Connection

redis_url = os.environ.get('REDIS_URL')
if redis_url is None:
    REDIS_QUEUE = None
else:
    conn = redis.from_url(redis_url)
    REDIS_QUEUE = Queue(connection=conn, default_timeout=3600)
