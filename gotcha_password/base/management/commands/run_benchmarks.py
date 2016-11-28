from django.core.management.base import BaseCommand, CommandError

import os, sys

from base.models import *
from base.redis_utils import REDIS_QUEUE

def run_benchmarks(login_attempt, log_progress):
    def log(msg='', newline=True):
        if log_progress:
            end = '\n' if newline else ''
            sys.stdout.write(msg + end)
            sys.stdout.flush()

    log('Running benchmarks for %s... ' % login_attempt, newline=False)

    # i-th index of lists represents benchmark with accuracy threshold=i
    benchmarks = {
        # algorithm to check password after logging in
        'check': [],
        # algorithm to brute force permutation
        'crack': [],
    }

    for i in range(7):
        log('#', newline=False)
        benchmarks['check'].append(login_attempt.check_password_timed(i, 24000))

    # limit attempts to run benchmarks in a reasonable amount of time
    max_threshold = 5 if (login_attempt.user.num_images > 5) else 7
    for i in range(max_threshold):
        log('#', newline=False)
        benchmarks['crack'].append(login_attempt.crack_permutation(i, 1))

    login_attempt.set_benchmarks(benchmarks)
    log()

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
