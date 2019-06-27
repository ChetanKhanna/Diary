from django.core.management.base import BaseCommand
from PS2.models import Station, Student, Week
import csv
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string

import random
import string, datetime
def randomString(stringLength=10):
	"""Generate a random string of fixed length """
	letters = string.ascii_lowercase
	return ''.join(random.choice(letters) for i in range(stringLength))
class Command(BaseCommand):

	def _create(self):

		for i in range (10,1000):
			Week.objects.get_or_create(
			week_no = i,
			user_id = Student.objects.get(student_id = '2015A3PS0142G'),
			learning = randomString(100),
			submissionDate = datetime.datetime.now()


		)
		# for i in range (10,1000):
		# 	Week.objects.get_or_create(
		# 	week_no = i,
		# 	user_id = Student.objects.get(student_id = '2015A3PS0008P'),
		# 	learning = randomString(100),
		# 	submissionDate = datetime.datetime.now()
		

		# )
	def handle(self, *args, **options):
		self._create()
