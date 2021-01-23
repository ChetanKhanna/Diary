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
                next(reader, None) # skipping the header row
                for line_no, column in enumerate(reader, 1):
                    try:
                        temp_password = get_random_string(8)	
                        student_email = column[3]
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
                            mentor_name = column[6],
                            mentor_id = column[9],
                            mentor_contact = column[7],
                            mentor_email = column[8],
                        )
                        print('Mentor created', end =" ")
                        if(User.objects.filter(username=column[9]).count() == 0):
                            temp_password = get_random_string(8)
                            created = UserIdPassword.objects.get_or_create(
                                user = User.objects.create_user(username=column[9],
                                password = temp_password,
                                email = column[8],
                                ),
                                token = user_roles['mentor'],
                            )
                            data_to_write = column[9] + ", " + str(temp_password) + "\n"
                            mentor_pasword_file.write(data_to_write)
                        created=Station.objects.get_or_create(
                            mentor=Mentor.objects.get(mentor_id=column[9]),
                            station_name=column[4],
                            station_address=column[4],
                        )
                        print('Station created', end =" ")
                        created = Student.objects.get_or_create(
                        station = Station.objects.get(station_name=column[4]),
                        student_id = column[0],
                        student_name = column[1],
                        student_email = student_email,
                        )
                        print('Student created')
                    except Exception as e:
                        print("Skipped line number:", line_no)
                        print(e)
            student_password_file.close()
            mentor_pasword_file.close()

        def handle(self, *args, **options):
            self._create()
