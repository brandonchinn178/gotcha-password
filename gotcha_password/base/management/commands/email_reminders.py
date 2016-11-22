from django.core.management.base import BaseCommand, CommandError
from django.utils.html import strip_tags
from django.utils.html_parser import HTMLParser
from django.template.loader import render_to_string
from django.core.mail import get_connection, EmailMultiAlternatives
from django.conf import settings
from django.utils import timezone

import os, sys
from datetime import timedelta

from base.models import *
from base.redis_utils import REDIS_QUEUE

def email_reminders(log_progress):
    def log(msg='', newline=True):
        if log_progress:
            end = '\n' if newline else ''
            sys.stdout.write(msg + end)
            sys.stdout.flush()

    users = User.objects.filter(logins=None)

    emails = []
    for user in users:
        html_content = render_to_string('email_reminders.html', {'user': user})
        text_content = HTMLParser().unescape(strip_tags(html_content))
        emails.append(EmailMultiAlternatives(
            to=[user.email],
            subject='[REMINDER] A Study on Image-Based Password Schemes',
            body=text_content,
            alternatives=[(html_content, 'text/html')],
        ))

    if settings.IS_HEROKU:
        get_connection().send_messages(emails)
    else:
        # if in development, print email to console instead
        print '----- EMAILS SENT -----\n'
        for email in emails:
            print email.message()
        print '-----------------------\n'

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        if REDIS_QUEUE is not None:
            REDIS_QUEUE.enqueue(email_reminders, log_progress=False)
            print 'Emailing reminders queued.'
        else:
            email_reminders(log_progress=True)
