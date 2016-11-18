from django.core.management.base import BaseCommand

from rq import Worker

from base.redis_utils import REDIS_QUEUE

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        if REDIS_QUEUE is not None:
            Worker(REDIS_QUEUE, connection=REDIS_QUEUE.connection).work()
