from django.core.management.base import BaseCommand
from PS2.models import Station, Student, Mentor, UserIdPassword
import csv
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string

class Command(BaseCommand):
	def _create(self):
		user_roles = {
			'student' : 0,
			'mentor' : 1,
		}

		student_password_file = open("studentPassword.txt", 'w', encoding='iso-8859-1')
		mentor_pasword_file = open("mentorPassword.txt", 'w')
		with open("data.csv") as data_file:
			reader = csv.reader(data_file)
			for column in reader:
				domain_name = ""
				temp_password = get_random_string(8)
				student_email = "f" + column[0][0:4] + column[0][8:12]
				if column[0][-1] == 'P':
					domain_name = "@pilani.bits-pilani.ac.in"
				if column[0][-1] == 'G':
					domain_name = "@goa.bits-pilani.ac.in"
				if column[0][-1] == 'H':
					domain_name = "@hyderabad.bits-pilani.ac.in"
				student_email = student_email + domain_name
				print(student_email, end= " ")
				created = UserIdPassword.objects.get_or_create(
					user = User.objects.create_user(username=column[0],
                    password = temp_password,
					email = student_email,
					),
					token = user_roles['student'],
				)
				print('UserID-Password created', end =" ")
				data_to_write = column[0] + ", " + str(temp_password) + "\n"
				student_password_file.write(data_to_write)

				created = Mentor.objects.get_or_create(
					mentor_name = column[4],
					mentor_id = column[5],
					mentor_contact = column[6],
					mentor_email = column[7],
				)
				print('Mentor created', end =" ")
				if(User.objects.filter(username=column[5]).count() == 0):
					temp_password = get_random_string(8)
					created = UserIdPassword.objects.get_or_create(
						user = User.objects.create_user(username=column[5],
	                    password = temp_password,
						email = column[7],
						),
						token = user_roles['mentor'],
					)
					data_to_write = column[5] + ", " + str(temp_password) + "\n"
					mentor_pasword_file.write(data_to_write)
				created=Station.objects.get_or_create(
					mentor=Mentor.objects.get(mentor_id=column[5]),
					station_name=column[2],
					station_address=column[3],
				)
				print('Station created', end =" ")
				created = Student.objects.get_or_create(
					station = Station.objects.get(station_name=column[2]),
					student_id = column[0],
					student_name = column[1],
					student_email = student_email,
				)
				print('Student created')
		student_password_file.close()
		mentor_pasword_file.close()

	def handle(self, *args, **options):
		self._create()
