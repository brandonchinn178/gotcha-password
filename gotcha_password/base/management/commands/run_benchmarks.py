from django.core.management.base import BaseCommand, CommandError

import os, sys, redis
from rq import Queue

from base.models import *

def run_benchmarks(log_progress):
    def log(msg='', newline=True):
        if log_progress:
            end = '\n' if newline else ''
            sys.stdout.write(msg + end)
            sys.stdout.flush()

    for login_attempt in LoginAttempt.objects.filter(benchmarks=None):
        log('Running benchmarks for %s... ' % login_attempt, newline=False)

        benchmarks = {
            # algorithm to check password after logging in
            'check': {
                # list, where i-th number represents benchmark with accuracy
                # threshold=i and iterations=1
                'accuracy': [-1 for i in range(7)],
                # list, where ith-number represents benchmark with iterations=(i + 1) * 25
                # and accuracy threshold=2
                'iterations': [-1 for i in range(10)],
            },
            # algorithm to brute force permutation
            'crack': {
                'accuracy': [-1 for i in range(7)],
                'iterations': [-1 for i in range(10)],
            },
        }
        for i in range(7):
            log('#', newline=False)
            benchmarks['check']['accuracy'][i] = login_attempt.check_password_timed(i, 1)
            benchmarks['crack']['accuracy'][i] = login_attempt.crack_permutation(i, 1)

        for i in range(10):
            log('#', newline=False)
            iterations = (i + 1) * 25
            benchmarks['check']['iterations'][i] = login_attempt.check_password_timed(2, iterations)
            benchmarks['crack']['iterations'][i] = login_attempt.crack_permutation(2, iterations)

        login_attempt.set_benchmarks(benchmarks)
        log()

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        redis_url = os.environ.get('REDIS_URL', None)
        if redis_url:
            conn = redis.from_url(redis_url)
            Queue(connection=conn).enqueue(run_benchmarks, log_progress=False)
            print 'Benchmarks queued.'
        else:
            run_benchmarks(log_progress=True)
