import os, redis, django
from rq import Worker, Queue, Connection

# activate django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gotcha_password.settings")
django.setup()

listen = ['high', 'default', 'low']

redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379')

conn = redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()
