from django.core.management.base import BaseCommand, CommandError
from django.core.files.storage import default_storage
from django.db.models import Min, Max, Avg, F
from django.utils.timezone import localtime

import os, sys, redis
from rq import Queue
from xlwt.Workbook import Workbook
from datetime import datetime

from base.models import *

def run_collect_data(log_progress):
    def log(msg='', newline=True):
        if log_progress:
            end = '\n' if newline else ''
            sys.stdout.write(msg + end)
            sys.stdout.flush()

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

    # Save a file with all the data as an Excel file
    log('Saving all data...')
    excel = Workbook()

    users_sheet = excel.add_sheet('Users')
    fields = ['timestamp', 'username', 'email', 'num_images']
    values = User.objects.values_list(*fields)
    for i, field in enumerate(fields):
        users_sheet.write(0, i, field)
    for i, user in enumerate(values):
        for j, val in enumerate(user):
            if isinstance(val, datetime):
                val = localtime(val).strftime('%m/%d/%Y %H:%M:%S')
            users_sheet.write(i + 1, j, val)

    logins_sheet = excel.add_sheet('Login Attempts')
    fields = ['timestamp', 'user__username', 'right_password', 'correct_images', 'percent_correct']
    values = LoginAttempt.objects.annotate(percent_correct=percent_correct).values_list(*fields)
    for i, field in enumerate(fields):
        logins_sheet.write(0, i, field)
    for i, login in enumerate(values):
        for j, val in enumerate(login):
            if isinstance(val, datetime):
                val = localtime(val).strftime('%m/%d/%Y %H:%M:%S')
            logins_sheet.write(i + 1, j, val)

    with default_storage.open('data.xls', 'w+') as f:
        excel.save(f)

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        redis_url = os.environ.get('REDIS_URL', None)
        if redis_url:
            conn = redis.from_url(redis_url)
            Queue(connection=conn).enqueue(run_collect_data, log_progress=False)
            print 'Collecting data queued.'
        else:
            run_collect_data(log_progress=True)
