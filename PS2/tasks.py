from __future__ import absolute_import, unicode_literals
from django.contrib.auth.models import User
from django.core import management
from PS2.models import Station, Student, Mentor, Week, UserIdPassword
from celery import shared_task, current_task, task
import csv
from django.utils.crypto import get_random_string
from celery_progress.backend import ProgressRecorder
import os
from django.conf import settings

BASE_DIR = settings.BASE_DIR

@shared_task(bind=True)
def downloadDatabaseAsCsv(self):
	# management.call_command('downloadDatabaseAsCsv')
	progress_recorder = ProgressRecorder(self)
	current_user=1
	total_user = len(Week.objects.all())
	if(total_user == 0) : 
		total_user = 1
	try:
		# finding name of file
		file_name = 'databaseEntriesAsCsv.csv'
		# folder_name = 'myproject'
		file_path = os.path.join(BASE_DIR, file_name)
		# writting headers to csv
		with open(file_path, 'w+', encoding='iso-8859-1') as databaseEntriesAsCsv:
			fieldnames = [
				'IDNumber','StudentName','Week_No',
				'Submission_Date','Tasks_Planned',
				'Tasks_Completed','Variation','Next_Week_Plan',
				'Learning','Equipments_Used','Mentor_Comments',
				'AllotedStaion','StationAddress','AllotedFaculty',
				'FacultyPSRNNo','FacultyContact','FacultyEmail'
				]
			entry_writer = csv.DictWriter(databaseEntriesAsCsv, fieldnames=fieldnames)
			entry_writer.writeheader()
		# writting data into csv
		with open(file_path, mode='a', encoding='iso-8859-1') as databaseEntriesAsCsv:
			entry_writer = csv.writer(databaseEntriesAsCsv, delimiter=',', quotechar='"',
			 quoting=csv.QUOTE_MINIMAL)
			for week in Week.objects.all() :
				toWrite = list()
				student = week.user_id
				station = student.station
				mentor = station.mentor
				# adding line to list
				toWrite.append(str(student.student_id))
				toWrite.append(str(student.student_name))
				toWrite.append(str(week.week_no))
				toWrite.append(str(week.submissionDate))
				toWrite.append(str(week.tasksplanned))
				toWrite.append(str(week.taskscompleted))
				toWrite.append(str(week.variation))
				toWrite.append(str(week.nextweek))
				toWrite.append(str(week.learning))
				toWrite.append(str(week.equipments))
				toWrite.append(str(week.comment))
				toWrite.append(str(station.station_name))
				toWrite.append(str(station.station_address))
				toWrite.append(str(mentor.mentor_name))
				toWrite.append(str(mentor.mentor_id))
				toWrite.append(str(mentor.mentor_contact))
				toWrite.append(str(mentor.mentor_email))
				# Write the writter object to file
				entry_writer.writerow(toWrite)
				# updating state of task
				current_task.update_state(state='PROGRESS',
					meta={'current':current_user, 'total': total_user})
				progress_recorder.set_progress(current_user, total_user)
				current_user = current_user + 1

		return {'current': total_user, 'total': total_user}
	except:
		current_task.update_state(state='FAILURE',
					meta={'current':-1, 'total': -1})
		progress_recorder.set_progress(-1, -1)
		return -1
		


	
@shared_task(bind=True)
def PopulateDataBase(self):
	current_user = 1
	try:
		# clearing existing DB schema
		management.call_command('clearModels')
		progress_recorder = ProgressRecorder(self)
		# # re-populating with new enteries
		# management.call_command('populateDB')
		# return 1
		user_roles = {
			'student' : 0,
			'mentor' : 1,
		}
		student_password_file = open("studentPassword.txt", 'w')
		mentor_pasword_file = open("mentorPassword.txt", 'w')
		# counting total users in current csv file
		with open("data.csv") as data_file:
			total_user = sum(1 for row in data_file)
		
		with open("data.csv") as data_file:
			reader = csv.reader(data_file)
			for column in reader:
				# print('in for loop')
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
				# print(student_email, end= " ")
				created = UserIdPassword.objects.get_or_create(
					user = User.objects.create_user(username=column[0],
					password = temp_password,
					email = student_email,
					),
					token = user_roles['student'],
				)
				# print('UserID-Password created', end =" ")
				data_to_write = column[0] + ", " + str(temp_password) + "\n"
				student_password_file.write(data_to_write)
				created = Mentor.objects.get_or_create(
					mentor_name = column[4],
					mentor_id = column[5],
					mentor_contact = column[6],
					mentor_email = column[7],
					)
				# print('Mentor created', end =" ")
				if(User.objects.filter(username=column[5]).count() == 0):
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
				# print('Station created', end =" ")
				created = Student.objects.get_or_create(
					station = Station.objects.get(station_name=column[2]),
					student_id = column[0],
					student_name = column[1],
					student_email = student_email,
				)
				# print('Student created')
				# updating state of task
				current_task.update_state(state='PROGRESS',
					meta={'current':current_user, 'total': total_user})
				progress_recorder.set_progress(current_user, total_user)
				current_user = current_user + 1

		return {'current': total_user, 'total': total_user}
	except:
		current_task.update_state(state='FAILURE',
					meta={'current':-1, 'total': -1})
		progress_recorder.set_progress(-1, -1)
		return -1 * current_user
