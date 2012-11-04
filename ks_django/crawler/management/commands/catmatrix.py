from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError
from crawler.models import *
from datetime import datetime, date
import urllib
import re
import sys

class Command(BaseCommand):

	def handle(self, *args, **options):
		