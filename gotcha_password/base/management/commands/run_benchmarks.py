from django.core.management.base import BaseCommand, CommandError

import os, sys

from base.models import *
from base.redis_utils import REDIS_QUEUE
from base.utils import run_benchmarks

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        login_attempts = LoginAttempt.objects.filter(benchmarks='')
        if REDIS_QUEUE is not None:
            for login_attempt in login_attempts:
                REDIS_QUEUE.enqueue(run_benchmarks, login_attempt, log_progress=False)
            print 'Benchmarks queued.'
        else:
            for login_attempt in login_attempts:
                run_benchmarks(login_attempt, log_progress=True)
