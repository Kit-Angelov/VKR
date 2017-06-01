from django.core.management.base import BaseCommand, CommandError
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'gamajunn.settings'
from gamajunn.nn import work


class Command(BaseCommand):

    def handle(self, *args, **options):
        work()

