from django.core.management.base import BaseCommand, CommandError
from django.core.files.storage import default_storage
from django.db.models import Min, Max, Avg, F
from django.utils.timezone import localtime

import os, sys
from xlwt.Workbook import Workbook
from datetime import datetime

from base.models import *
from base.redis_utils import REDIS_QUEUE

class ExcelSheet(object):
    """
    An object wrapping a Worksheet to abstract writing rows. Usage:

    ExcelSheet(workbook, 'User')
    """
    def __init__(self, workbook, name):
        self.sheet = workbook.add_sheet(name)
        self.row = 1 # headers are row 0

    def write_headers(self, labels):
        for i, label in enumerate(labels):
            self.sheet.write(0, i, label)

    def add_row(self, row):
        for j, val in enumerate(row):
            if isinstance(val, datetime):
                val = localtime(val).strftime('%m/%d/%Y %H:%M:%S')
            self.sheet.write(self.row, j, val)

        self.row += 1

    def add_rows(self, rows):
        for row in rows:
            self.add_row(row)

def run_collect_data(log_progress):
    def log(msg='', newline=True):
        if log_progress:
            end = '\n' if newline else ''
            sys.stdout.write(msg + end)
            sys.stdout.flush()

    # Save a file with summary statistics
    log('Saving summary stats...')
    percent_correct = F('correct_images') / F('user__num_images')
    percentages = LoginAttempt.objects.filter(right_password=True
        ).annotate(percent_correct=percent_correct
        ).order_by('percent_correct'
        ).values_list('percent_correct', flat=True
        )
    total = len(percentages)
    middle = total / 2 - 1
    if total % 2 == 0:
        median = sum(percentages[middle:middle+2]) / 2
    else:
        median = percentages[middle]

    with default_storage.open('summary.txt', 'w') as f:
        f.write('\n'.join([
            'Total accounts: %d' % User.objects.count(),
            'Total login attempts: %d' % LoginAttempt.objects.count(),
            'Total login attempts with invalid passwords: %d' % LoginAttempt.objects.filter(right_password=False).count(),
            'Min percentage: %f' % percentages[0],
            'Max percentage: %f' % percentages[total - 1],
            'Average percentage: %f' % (sum(percentages) / float(total)),
            'Median percentage: %f' % median,
        ]))

    # Save a file with all the data as an Excel file
    log('Saving all data...')
    workbook = Workbook()

    users_sheet = ExcelSheet(workbook, 'Users')
    fields = ['timestamp', 'username', 'email', 'num_images']
    values = User.objects.values_list(*fields)
    users_sheet.write_headers(fields)
    users_sheet.add_rows(values)

    logins_sheet = ExcelSheet(workbook, 'Login Attempts')
    logins_sheet.write_headers(['Timestamp', 'Username', 'Right password?', '# correct images', '# total images', 'Percent correct'])
    images_accuracy = ExcelSheet(workbook, 'NumImages_Accuracy')
    images_accuracy.write_headers(['Number of Images', 'Percent Correct'])
    check_sheet = ExcelSheet(workbook, 'Check')
    check_sheet.write_headers(['Number of Images', 'Accuracy Threshold', 'Time', 'Right password'])
    crack_sheet = ExcelSheet(workbook, 'Crack')
    crack_sheet.write_headers(['Number of Images', 'Accuracy Threshold', 'Time'])
    for login in LoginAttempt.objects.annotate(percent_correct=percent_correct):
        num_images = login.user.num_images

        logins_sheet.add_row([
            login.timestamp,
            login.user.username,
            login.right_password,
            login.correct_images,
            num_images,
            login.percent_correct
        ])
        if login.right_password:
            # only run accuracy for logins with the right password
            images_accuracy.add_row([num_images, login.percent_correct])

        try:
            benchmarks = login.get_benchmarks()
        except:
            continue

        for threshold, time in enumerate(benchmarks['check']):
            check_sheet.add_row([num_images, threshold, time, login.right_password])
        for threshold, time in enumerate(benchmarks['crack']):
            crack_sheet.add_row([num_images, threshold, time])

    with default_storage.open('data.xls', 'w+') as f:
        workbook.save(f)

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        if REDIS_QUEUE is not None:
            REDIS_QUEUE.enqueue(run_collect_data, log_progress=False)
            print 'Collecting data queued.'
        else:
            run_collect_data(log_progress=True)
