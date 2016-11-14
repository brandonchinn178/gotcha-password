from django.core.management.base import BaseCommand, CommandError
from django.core.files.storage import default_storage
from django.db.models import Min, Max, Avg, F

from rq import Queue
import os, sys, redis

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

    # Save a file with summary statistics
    log('Saving summary stats...')
    percent_correct = F('correct_images') / F('user__num_images')
    percentages = LoginAttempt.objects.filter(right_password=True).annotate(
        percent_correct=percent_correct).order_by('percent_correct').values_list('percent_correct', flat=True)
    total = len(percentages)
    middle = total / 2 - 1
    if total % 2 == 0:
        median = percentages[middle]
    else:
        median = sum(percentages[middle:middle+1]) / 2
    
    with default_storage.open('summary.txt', 'w+') as f:
        f.writelines('\n'.join([
            'Total accounts: %d' % User.objects.count(),
            'Total login attempts with invalid passwords: %d' % LoginAttempt.objects.filter(right_password=False).count(),
            'Min percentage: %f' % percentages[0],
            'Max percentage: %f' % percentages[total - 1],
            'Average percentage: %f' % (sum(percentages) / float(total)),
            'Median percentage: %f' % median,
        ]))

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        redis_url = os.environ.get('REDIS_URL', None)
        if redis_url:
            conn = redis.from_url(redis_url)
            Queue(connection=conn).enqueue(run_benchmarks, log_progress=False)
            print 'Benchmarks queued.'
        else:
            run_benchmarks(log_progress=True)
