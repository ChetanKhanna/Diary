from django.core.management.base import BaseCommand
from PS2.models import *
import csv, random
from django.contrib.auth.models import User

class Command(BaseCommand):
	with open('databaseEntriesAsCsv.csv', mode='w') as databaseEntriesAsCsv:
		fieldnames = ['IDNumber','StudentName','Week_No','Submission_Date','Tasks_Planned','Tasks_Completed','Variation','Next_Week_Plan','Learning','Equipments_Used','Mentor_Comments','AllotedStaion','StationAddress','AllotedFaculty','FacultyPSRNNo','FacultyContact','FacultyEmail']
		entry_writer = csv.DictWriter(databaseEntriesAsCsv, fieldnames=fieldnames)
		entry_writer.writeheader()
	with open('databaseEntriesAsCsv.csv', mode='a') as databaseEntriesAsCsv:
		entry_writer = csv.writer(databaseEntriesAsCsv, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)		
		for week in Week.objects.all() :
			toWrite = list()
			student = week.user_id
			station = student.station
			mentor = station.mentor
			toWrite.append(student.student_id)
			toWrite.append(student.student_name)
			toWrite.append(week.week_no)
			toWrite.append(week.submissionDate)
			toWrite.append(week.tasksplanned)
			toWrite.append(week.taskscompleted)
			toWrite.append(week.variation)
			toWrite.append(week.nextweek)
			toWrite.append(week.learning)
			toWrite.append(week.equipments)
			toWrite.append(week.comment)
			# toWrite.append(week.lock)
			toWrite.append(station.station_name)
			toWrite.append(station.station_address)
			toWrite.append(mentor.mentor_name)
			toWrite.append(mentor.mentor_id)
			toWrite.append(mentor.mentor_contact)
			toWrite.append(mentor.mentor_email)
			# print(toWrite)
			entry_writer.writerow(toWrite)



