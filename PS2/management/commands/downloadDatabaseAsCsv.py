from django.core.management.base import BaseCommand
from PS2.models import Week
import csv
import os
from django.conf import settings

BASE_DIR = settings.BASE_DIR

class Command(BaseCommand):
	def _create(self):
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
		return 1

	def handle(self, *args, **options):
		self._create()
