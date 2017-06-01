from django.core.management.base import BaseCommand, CommandError
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'gamajunn.settings'
from gamajunn.classificator import classification_command


class Command(BaseCommand):

    def handle(self, *args, **options):
        classification_command()
