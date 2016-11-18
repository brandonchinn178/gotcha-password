import os, redis, django
from rq import Worker, Queue, Connection

# activate django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gotcha_password.settings")
django.setup()

redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379')

conn = redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker([
            Queue(priority, default_timeout=3600*24)
            for priority in ['high', 'default', 'low']
        ])
        worker.work()
