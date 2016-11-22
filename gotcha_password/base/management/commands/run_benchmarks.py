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

    # generating permutations is expensive; limit if user's num_images gets too high
    crack_accuracy = 7 if login_attempt.user.num_images < 6 else 4
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
            'accuracy': [-1 for i in range(crack_accuracy)],
            'iterations': [-1 for i in range(10)],
        },
    }
    for i in range(7):
        log('#', newline=False)
        benchmarks['check']['accuracy'][i] = login_attempt.check_password_timed(i, 1)

    for i in range(crack_accuracy):
        log('#', newline=False)
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
        login_attempts = LoginAttempt.objects.filter(benchmarks='')
        if REDIS_QUEUE is not None:
            for login_attempt in login_attempts:
                REDIS_QUEUE.enqueue(run_benchmarks, login_attempt, log_progress=False)
            print 'Benchmarks queued.'
        else:
            for login_attempt in login_attempts:
                run_benchmarks(login_attempt, log_progress=True)
