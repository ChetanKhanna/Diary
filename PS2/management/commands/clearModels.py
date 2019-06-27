from django.core.management.base import BaseCommand
from PS2.models import Mentor, Week, Student, Station, UserIdPassword
from django.contrib.auth.models import User

class Command(BaseCommand):
	def _create(self):
		Mentor.objects.all().delete()
		Week.objects.all().delete()
		Student.objects.all().delete()
		Station.objects.all().delete()
		UserIdPassword.objects.all().delete()
		User.objects.all().exclude(is_staff=True, is_superuser=True).delete()

	def handle(self, *args, **options):
		self._create()



