from django.core.management.base import BaseCommand, CommandError
#from django.db import IntegrityError
#from django.db import transaction
from crawler.models import *


class Command(BaseCommand):
    def handle(self, *args, **options):
        c = Cursor()
        c.id = 2
        c.backer_id = 1
        c.save();