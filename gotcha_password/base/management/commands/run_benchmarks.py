from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from base.models import *
from base.utils import run_benchmarks

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        for login_attempt in LoginAttempt.objects.filter(benchmarks=''):
            run_benchmarks(login_attempt, log_progress=not settings.IS_HEROKU)
