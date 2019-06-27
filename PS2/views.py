# importing important modules
# importing django modules
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.core import management
from django.shortcuts import render
from django.views import generic
from django.shortcuts import redirect
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
# importing reportlab modules
from reportlab.platypus import PageBreak
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image 
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
# importing celery modules
from celery.result import AsyncResult
# importing other important modules
from threading import Thread
import time
import os
from zipfile import ZipFile
# importing models of PS2
from . models import Student, Station, Mentor, Week, UserIdPassword
# importing tasks of PS2
from PS2.tasks import PopulateDataBase, downloadDatabaseAsCsv

BASE_DIR = settings.BASE_DIR

## Views for PS2
class HomeView(generic.TemplateView):
	template_name = 'PS2/home.html'

class RedirectView(generic.TemplateView):
	# request.GET call 
	def get(self, request, *args, **kwargs):
		# Check to see if user credentials in UserIdPassword table
		try:
			current_user = request.user
			user_object = UserIdPassword.objects.get(user=current_user)
			if user_object.token == 0:
				return redirect('/PS2/student')
			elif user_object.token == 1:
				return redirect('/PS2/mentor')
		except ObjectDoesNotExist:
			# Check if user credentials match any admin/staff
			if current_user.is_superuser or current_user.is_staff:
				return redirect('/PS2/psd')
			# Redirect to login page for re-entry
			else:
				return redirect('/PS2/login')

class StudentEntryView(generic.TemplateView):
	template_name = 'PS2/student.html'

	def get(self, request, *args, **kwargs):
		current_user=request.user
		if(current_user.is_authenticated):
			# If current user if student
			if(UserIdPassword.objects.get(user=current_user).token==0):
				# collecting context data to be passed to template html file
				student_object=Student.objects.get(student_id=current_user)
				mentor_object = student_object.station.mentor
				station_object = student_object.station
				weeks = Week.objects.filter(user_id=student_object)
				weeks_data = [(week.week_no, week.lock) for week in weeks]
				weeks_data.reverse()
				# context data collected is stored in params dict
				params = {
				'student': student_object,
				'mentor': mentor_object,
				'station': station_object,
				'weeks_data': weeks_data}
				# render template with collected context data
				return render(request, self.template_name, params)
			else:
				return redirect('../mentor')
		else:
			return redirect('/PS2/login')


class MentorEntryView(generic.TemplateView):

	def get(self, request, *args, **kwargs):
		current_user = request.user
		if(current_user.is_authenticated):
			if(UserIdPassword.objects.get(user=current_user).token == 1):
				mentor_object = Mentor.objects.get(mentor_id = current_user)
				return render(request, 'PS2/mentor.html', {
					'stations':Station.objects.filter(mentor = mentor_object),
					'mentor':mentor_object,})
			else:
				return redirect('../student')
		else:
			return redirect('/PS2/login')

class Weeks(generic.TemplateView):
	# template_name = 'PS2/weeks.html'
	def get(self, request, *args, **kwargs):
		current_user = request.user
		if current_user.is_authenticated:
			if UserIdPassword.objects.get(user=current_user).token == 0:
				student_object = Student.objects.get(student_id=current_user)
				try:
					# Get parameter weeks/id If doesn't exist render weeks.html view
					__week_no = int(kwargs['id'])
					# If week id = 0 then new entry is to be added
					if __week_no == 0:
						week_data = {'week_no' : 0}		#Send dummmy to allow redirects to post
						return render(request,'PS2/weeks.html', {'week_data' : week_data,
							'student':student_object,})
					# TODO : Insert strict check on number of weeks actually completed
					# If week/<id> where if less than 90 then render that week number
					elif __week_no <= 90:
						week_data = Week.objects.get(week_no = __week_no, user_id = current_user.username)
						return render(request, 'PS2/weeks.html', {'week_data' : week_data,'student':student_object,})
					else:
						return render(request,'PS2/weeks.html')

				except KeyError:
					return render(request,'PS2/weeks.html')
			else:
				return redirect('../mentor')
		else:
			return redirect('/PS2/login')

	def post(self, request, *args, **kwargs):
		current_user=request.user
		__week_no = int(kwargs['id'])
		if(current_user.is_authenticated):
			if UserIdPassword.objects.get(user=current_user).token == 0:
				if request.POST.get("goBack"):
					return redirect('/PS2/student')
				# collecting enteries POSTed by user
				post_tasksplanned = request.POST.get('tasksplanned')
				post_taskscompleted = request.POST.get('taskscompleted')
				post_variation = request.POST.get('variation')
				post_nextweek = request.POST.get('nextweek')
				post_learning = request.POST.get('learning')
				post_equipments = request.POST.get('equipments')
				# Counting week enteries of students
				count = Week.objects.filter(user_id=Student
					.objects.get(student_id = current_user)).count()
				if __week_no == 0:
					week_data_exists = False
					try:
					    week_data_exists = Week.objects.get(user_id=Student.objects.get(student_id = current_user),
							tasksplanned = post_tasksplanned,
							taskscompleted = post_taskscompleted,
							variation = post_variation,
							nextweek = post_nextweek,
							learning = post_learning,
							equipments = post_equipments,

							)
					except:
					    _ = Week.objects.get_or_create(
							week_no = count + 1,
							user_id = Student.objects.get(student_id = current_user),
							tasksplanned = post_tasksplanned,
							taskscompleted = post_taskscompleted,
							variation = post_variation,
							nextweek = post_nextweek,
							learning = post_learning,
							equipments = post_equipments,
							submissionDate = timezone.now()
						)

					if week_data_exists:
						return redirect('/PS2/student')

				else:
					old_week_object = Week.objects.get(week_no = __week_no,	user_id = Student.objects.get(student_id = current_user) )
					old_week_object.tasksplanned = post_tasksplanned
					old_week_object.taskscompleted = post_taskscompleted
					old_week_object.variation = post_variation
					old_week_object.nextweek = post_nextweek
					old_week_object.learning = post_learning
					old_week_object.equipments = post_equipments
					old_week_object.submissionDate = timezone.now()

					old_week_object.save()

				return redirect('/PS2/student')
			else:
				return redirect('../mentor')
		else:
			return redirect('/PS2/login')




class Students_alloted_to_mentor(generic.TemplateView):
	template_name = 'PS2/students_alloted_to_mentor.html'

	def get(self, request, *args, **kwargs):
		print(kwargs['station'])
		station=kwargs['station']
		current_user = request.user
		if current_user.is_authenticated:
			# if current user is a mentor
			if UserIdPassword.objects.get(user=current_user).token == 1:
				student_under_mentor = Student.objects.filter(station = Station
					.objects.get(station_name=station))
				return render(request, 'PS2/students_alloted_to_mentor.html',
					{'students':student_under_mentor,
					'mentor': Mentor.objects.get(mentor_id = current_user),
					'station':station},)
			else:
				return redirect('../student')
		else:
			return redirect('/PS2/login')

class Mentor_view_of_weeks(generic.TemplateView):
	template_name = 'PS2/mentor_view_of_weeks.html'

	def get(self, request, *args, **kwargs):
		current_user = request.user
		if current_user.is_authenticated:
			if UserIdPassword.objects.get(user=current_user).token == 1:
				# collecting data from url
				student=kwargs['student']
				station=kwargs['station']
				count=Week.objects.filter(user_id=Student.objects.get(student_name=student)).count()
				mentor_object = Mentor.objects.get(mentor_id = current_user)
				weeks = (Week.objects.filter(user_id=Student
						.objects
						.get(student_name=student)))
				# wrapping relevant datafields in a tuple -- template doen't needs
				# entire week data for all weeks
				weeks_data = [(week.week_no, week.lock, week.submissionDate)
					for week in weeks]
				# To display enteries from newsest to oldest we reverse the order
				weeks_data.reverse()
				params = {'enteries':range(count),
					'station':station,
					'student':student,
					'mentor': mentor_object,
					'weeks_data': weeks_data
					}
				return render(request, self.template_name, params)
			else:
				return redirect('../student')
		else:
			return redirect('PS2/accounts/login')

	def post(self, request, *args, **kwargs):
		return redirect('/PS2/mentor/'+station)


class Lock(generic.TemplateView):
	def get(self, request, *args, **kwargs):
		current_user = request.user
		if current_user.is_authenticated:
			if UserIdPassword.objects.get(user=current_user).token == 1:
				station=kwargs['station']
				student=kwargs['student']
				enteryNumber=kwargs['enteryNumber']
				week_object = Week.objects.get(week_no = enteryNumber,user_id = Student.objects.get(student_name=student) )
				# setting lock attribute --> 1 : Entry Locked
				week_object.lock=1
				week_object.save()
				return redirect('/PS2/mentor/'+station+'/'+student)
			else:
				return redirect('../student')
		else:
			return redirect('PS2/accounts/login')

class UnLock(generic.TemplateView):
	def get(self, request, *args, **kwargs):
		current_user = request.user
		if current_user.is_authenticated:
			if UserIdPassword.objects.get(user=current_user).token == 1:
				station=kwargs['station']
				student=kwargs['student']
				enteryNumber=kwargs['enteryNumber']
				week_object = Week.objects.get(week_no = enteryNumber,user_id = Student.objects.get(student_name=student) )
				# setting attribute --> 0: Entry unlocked (editable)
				week_object.lock=0
				week_object.save()
				return redirect('/PS2/mentor/'+station+'/'+student)
			else:
				return redirect('../student')
		else:
			return redirect('PS2/accounts/login')


class Mentor_view_of_entry(generic.TemplateView):
	template_name = 'PS2/mentor_view_of_entry.html'
	def get(self, request, *args, **kwargs):
		current_user = request.user
		if current_user.is_authenticated:
			if UserIdPassword.objects.get(user=current_user).token == 1:
				# collecting relevant data from url
				station=kwargs['station']
				student=kwargs['student']
				enteryNumber=kwargs['enteryNumber']
				# Week enteries for current student
				week_object = Week.objects.get(week_no = enteryNumber,
						user_id = Student.objects.get(student_name=student) )
				# rendering template
				return render(request, 'PS2/mentor_view_of_entry.html',
					{'tasksplanned':week_object.tasksplanned,
					'taskscompleted':week_object.taskscompleted,
					'variation':week_object.variation,
					'nextweek':week_object.nextweek,
					'learning':week_object.learning,
					'equipments':week_object.equipments,
					'comment':week_object.comment,
					'lock':week_object.lock,
					'mentor': Mentor.objects.get(mentor_id = current_user),
					'week':week_object,
					'station':station,
					'student':student,
					'enteryNumber':enteryNumber,
					},)
			else:
				return redirect('../student')
		else:
			return redirect('PS2/accounts/login')

	def post(self, request, *args, **kwargs):
		current_user=request.user
		if(current_user.is_authenticated):
			if UserIdPassword.objects.get(user=current_user).token == 1:
				station=kwargs['station']
				student=kwargs['student']
				enteryNumber=kwargs['enteryNumber']

				week_object = Week.objects.get(week_no = enteryNumber,
						user_id = Student.objects.get(student_name=student) )
				# collecting POSTed data
				# Submit only : default status for week entry is 0 --> Unlocked
				if request.POST.get("Submit"):
					week_object.comment = request.POST.get('comments')
				# Submit and lock week attribute
				elif request.POST.get("SubmitAndLock"):
					week_object.lock=1
					week_object.comment = request.POST.get('comments')
				elif request.POST.get("SubmitAndUnlock"):
					week_object.lock=0
					week_object.comment = request.POST.get('comments')

				week_object.save()

				return redirect('/PS2/mentor/'+station)

			else:
				return redirect('../student')
		else:
			return redirect('/PS2/login')


class Student_profile(generic.TemplateView):
	# template_name = 'PS2/student_profile.html'
	def pdf_view(self,request, student_object, *args, **kwargs):
		## Generating pdf of student profile using report-lab
		week_objects=Week.objects.filter(user_id=student_object)
		# storing pdf as '<student_id>.pdf'
		file_name = student_object.student_id
		doc = SimpleDocTemplate("/tmp/{}.pdf".format(file_name))
		# dict for storing formatting stlyes
		styles = getSampleStyleSheet()
		# initializing Story list
		Story = []
		# Adding image
		img = Image(BASE_DIR + '/logo.png', 3.5*inch, 3.5*inch)
		img.hAlign = 'CENTRE'
		Story.append(img)
		# Adding blank lines
		for _ in range(5):
			Story.append(Spacer(1,0.2*inch))
		# selecting style from styles dict
		text_style = styles["Title"]
		text_style.fontSize = 25
		bogustext = 'PS-Diary'
		pH = Paragraph(bogustext, text_style)
		Story.append(pH)
		for _ in range(10):
			Story.append(Spacer(1,0.2*inch))
		bogustext = (str(student_object.student_name))
		pH = Paragraph(bogustext, text_style)
		Story.append(pH)
		for _ in range(2):
			Story.append(Spacer(1,0.2*inch))
		text_style.fontSize = 25
		bogustext = (str(student_object.student_id))
		pH = Paragraph(bogustext, text_style)
		Story.append(pH)
		# Moving to next page
		Story.append(PageBreak())
		# Printing all enteries for current student
		for week_object in week_objects:
			text_style = styles["Title"]
			text_style.fontSize = 15
			bogustext = ("Entry " + str(week_object.week_no))
			pH = Paragraph(bogustext, text_style)
			Story.append(pH)
			Story.append(Spacer(1,0.2*inch))

			text_style = styles["Normal"]
			text_style.fontSize = 10
			bogustext = ("<strong><u>Tasks Planned for Week</u>:</strong> " + week_object.tasksplanned)
			p = Paragraph(bogustext, text_style)
			Story.append(p)
			Story.append(Spacer(1,0.2*inch))

			bogustext = ("<strong><u>Tasks Completed</u>:</strong> " + week_object.taskscompleted)
			p = Paragraph(bogustext, text_style)
			Story.append(p)
			Story.append(Spacer(1,0.2*inch))

			bogustext = ("<strong><u>Variation in Plan & Plan to Overcome them(if any)</u>:</strong> " + week_object.variation)
			p = Paragraph(bogustext, text_style)
			Story.append(p)
			Story.append(Spacer(1,0.2*inch))

			bogustext = ("<strong><u>Activities for Next Week</u>:</strong> " + week_object.nextweek)
			p = Paragraph(bogustext, text_style)
			Story.append(p)
			Story.append(Spacer(1,0.2*inch))

			bogustext = ("<strong><u>Learning Outcomes</u>:</strong> " + week_object.learning)
			p = Paragraph(bogustext, text_style)
			Story.append(p)
			Story.append(Spacer(1,0.2*inch))

			bogustext = ("<strong><u>Equipments/Software Used/Learnt</u>:</strong> " + week_object.equipments)
			p = Paragraph(bogustext, text_style)
			Story.append(p)
			Story.append(Spacer(1,0.2*inch))

			bogustext = ("<strong><u>Mentor's Comments</u>:</strong> " + week_object.comment)
			p = Paragraph(bogustext, text_style)
			Story.append(p)
			Story.append(Spacer(1,0.2*inch))
			# Moving to next page
			Story.append(PageBreak())

		doc.build(Story)

		fs = FileSystemStorage("/tmp")
		with fs.open("{}.pdf".format(file_name)) as pdf:
			response = HttpResponse(pdf, content_type='application/pdf')
			response['Content-Disposition'] = 'attachment; filename="{}.pdf"'.format(file_name)
			return response

		return response

	def get(self, request, *args, **kwargs):
		current_user = request.user
		if current_user.is_authenticated:
			hide = int(kwargs['hide'])
			if UserIdPassword.objects.get(user=current_user).token == 0:
				# Here current_user is student
				student_object = Student.objects.get(student_id = current_user)
				station_object = Station.objects.get(station_name = student_object.station)
				mentor_object = Mentor.objects.get(mentor_id = station_object.mentor)
				return render(request, 'PS2/student_profile.html',
							{'is_student':1,
							'hide_student':hide,
							'student_object':student_object,
							'mentor_object':mentor_object,
							'station_object':station_object,})
			elif UserIdPassword.objects.get(user=current_user).token == 1:
				student_object=""
				if not hide :
					student_name = kwargs['student']
					student_object = Student.objects.get(student_name = student_name)

				# Each student will have one faculty mentor : Use get
				mentor_object = Mentor.objects.get(mentor_id = current_user)
				# Each mentor may have one or more stations : Use filter
				station_object = Station.objects.filter(mentor = mentor_object)
				return render(request, 'PS2/student_profile.html',
							{'is_student':0,
							'hide_student':hide,
							'student_object':student_object,
							'mentor_object':mentor_object,
							 'station_object':station_object,})


	def post(self, request, *args, **kwargs):
		current_user=request.user
		if(current_user.is_authenticated):
			# Defining and accepting fields submittable by students
			if request.POST.get("submit_student") and UserIdPassword.objects.get(user=current_user).token == 0:
				# Collecting details
				student_name = kwargs['student']
				organization_contact = request.POST.get('organization_contact')
				organization_email_id = request.POST.get('organization_email_id')
				organization_mentor = request.POST.get('organization_mentor')
				# making student object
				student_object = Student.objects.get(student_name = student_name)
				# filling details in data tables
				student_object.organization_mentor = organization_mentor
				student_object.organization_email_id = organization_email_id
				student_object.organization_contact = organization_contact
				# saving details
				student_object.save()
				# rendering page
				return redirect('/PS2/student_profile/0/{}'.format(student_name))

			if request.POST.get("submit_student_phone") and UserIdPassword.objects.get(user=current_user).token == 0:
				student_name = kwargs['student']
				student_contact = request.POST.get('student_contact')
				# making student object
				student_object = Student.objects.get(student_name = student_name)
				# filling details in data tables
				student_object.student_contact = student_contact
				# saving details
				student_object.save()
				# rendering page
				return redirect('/PS2/student_profile/0/{}'.format(student_name))


			elif request.POST.get("submit_mentor") and UserIdPassword.objects.get(user=current_user).token == 1:
				mentor_contact = request.POST.get('mentor_contact')

				mentor_object = Mentor.objects.get(mentor_id = current_user)

				mentor_object.mentor_contact = mentor_contact
				mentor_object.save()

				return redirect(request,"/PS2/student")

			elif request.POST.get("downloadDiary"):
				student_name = kwargs['student']
				student_object = Student.objects.get(student_name = student_name)
				print(student_object)
				return self.pdf_view(request,student_object)
			else :
				return redirect('/PS2/')

class DownloadProgress(generic.TemplateView):

	def get(self, request, *args,**kwargs):
		task_id = kwargs['task_id']
		result = AsyncResult(task_id)
		
		redirect_id = kwargs['redirect_id']
		if redirect_id == 1:
			redirect_id = 0
		else :
			redirect_id = 1

		if result.state == 'SUCCESS':
			if result.info == -1:
				return HttpResponse("<h3>Error in data.csv, <a href=\"/PS2/psd\"> click here</a> to return. </h3>")
			
			return render(request, 'PS2/download_progress.html', context = {
			'result_state': result.state,
			'result_current': result.info['current'],
			'result_total': result.info['total'],
			'result_percent': ((result.info['current']/result.info['total'])
				*100),
			'redirect_id':redirect_id,
			'task_id':task_id,
			})
		elif result.state == 'PROGRESS':
			return render(request, 'PS2/download_progress.html', context = {
			'result_state': result.state,
			'result_current': result.info['current'],
			'result_percent': ((result.info['current']/result.info['total'])
				*100),
			'result_total': result.info['total'],
			'redirect_id':redirect_id,
			'task_id':task_id,
			})
		elif result.state == 'PENDING':
			time.sleep(1)
			return render(request, 'PS2/download_progress.html', context = {
			'result_state': result.state,
			'result_current': 1,
			'result_total': 1,
			'result_percent': 0,
			'redirect_id':redirect_id,
			'task_id':task_id,
			})	

		return HttpResponse("<h1> Error please try again </h1>")

	def post(self, request, *args, **kwargs):
		filename = 'databaseEntriesAsCsv.csv'
		path = os.path.join(BASE_DIR, filename)
		file_path = os.path.join(settings.MEDIA_ROOT, path)
		file_path = path
		# Deleting file from system using another thread
		# t = Thread(target = self.deleteTempFile, args=(path,))
		# t.start()
		# Changing response object
		
		with open(file_path, 'rb') as fh:
			response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
			response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
			return response
		return HttpResponse("<h1> Download : Error please try again </h1>")		


class UploadProgess(generic.TemplateView):

	def get(self, request, *args,**kwargs):
		task_id = kwargs['task_id']
		result = AsyncResult(task_id)
		
		redirect_id = kwargs['redirect_id']
		if redirect_id == 1:
			redirect_id = 0
		else :
			redirect_id = 1

		if type(result.info) == int and result.info < 0:
			temp = -1*result.info
			return HttpResponse("<h3>Error in data.csv at line "+str(temp)+" <a href=\"/PS2/psd\">click here</a> to return. </h3>")
			
		if result.state == 'SUCCESS':
			if type(result.info) == int and result.info < 0:
				temp = -1*result.info
				return HttpResponse("<h3>Error in data.csv at line "+str(temp)+" <a href=\"/PS2/psd\">click here</a> to return. </h3>")
			else:
				return render(request, 'PS2/upload_progress.html', context = {
				'result_state': result.state,
				'result_current': result.info['current'],
				'result_total': result.info['total'],
				'result_percent': ((result.info['current']/result.info['total'])
					*100),
				'redirect_id':redirect_id,
				'task_id':task_id,
				})
		elif result.state == 'PROGRESS':
			if type(result.info) == int and result.info < 0:
				temp = -1*result.info
				return HttpResponse("<h3>Error in data.csv at line "+str(temp)+" <a href=\"/PS2/psd\">click here</a> to return. </h3>")
			else:
				return render(request, 'PS2/upload_progress.html', context = {
				'result_state': result.state,
				'result_current': result.info['current'],
				'result_percent': ((result.info['current']/result.info['total'])
					*100),
				'result_total': result.info['total'],
				'redirect_id':redirect_id,
				'task_id':task_id,
				})
		elif result.state == 'PENDING':
			time.sleep(1)
			if type(result.info) == int and result.info < 0:
				temp = -1*result.info
				return HttpResponse("<h3>Error in data.csv at line "+str(temp)+" <a href=\"/PS2/psd\">click here</a> to return. </h3>")
			else: 
				return render(request, 'PS2/upload_progress.html', context = {
				'result_state': result.state,
				'result_current': 1,
				'result_total': 1,
				'result_percent': 0,
				'redirect_id':redirect_id,
				'task_id':task_id,
				})	
		if type(result.info) == int and result.info < 0:
			temp = -1*result.info
			return HttpResponse("<h3>Error in data.csv at line "+str(temp)+" <a href=\"/PS2/psd\">click here</a> to return. </h3>")
		

		return HttpResponse("<h1> Error please try again </h1>")

	def post(self, request, *args, **kwargs):
		return HttpResponse("<h1> post : Error please try again </h1>")		

class PSD(generic.TemplateView):
	# template_name = 'PS2/psd.html'
	def get(self, request, *args, **kwargs):
		current_user = request.user
		if current_user.is_staff or current_user.is_superuser:
			return render(request,'PS2/psd.html')

	def deleteTempFile(self, file_path):
		# Delete file with file_name from given path if exists
		tempFile = open(file_path,'w+')
		tempFile.write("")
		tempFile.close()
		return

	def post(self, request, *args, **kwargs):
		current_user = request.user
		if current_user.is_staff or current_user.is_superuser:
			# DOWNLOAD
			if request.POST.get("download"):
				task = downloadDatabaseAsCsv.delay()
				return redirect("/PS2/psd/download_progress/"+str(task.id)+"/0")
				
				# result = AsyncResult(task.id)

				# filename = 'databaseEntriesAsCsv.csv'
				# path = os.path.join(BASE_DIR, filename)
				# file_path = os.path.join(settings.MEDIA_ROOT, path)
				# file_path = path
				# # Deleting file from system using another thread
				# # t = Thread(target = self.deleteTempFile, args=(path,))
				# # t.start()
				# # Changing response object
				# with open(file_path, 'rb') as fh:
				# 	response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
				# 	response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
				# 	return response
				# # render the template again
				# return redirect('/PS2/psd/')
			# ERASE
			elif request.POST.get("erase"):
				# Erase database
				management.call_command('clearModels')
				return redirect('/PS2/psd/')
			# UPLOAD
			elif request.FILES['myfile']: 
				#DELETE data.csv IF ALREADY EXISTS
				fs = FileSystemStorage()
				# getting file 'data.csv'
				## Name of the file is hard-coded to accept only 'data.csv'.
				## No other file name would work.
				filename = 'data.csv'
				# folder = 'myproject'
				file = os.path.join(BASE_DIR, filename)				
				if fs.exists(file):
					os.remove(file)
				# UPLOAD CODE
				myfile = request.FILES['myfile']
				fs = FileSystemStorage()
				filename = fs.save(myfile.name, myfile)
				# POPULATE DATABASE
				task = PopulateDataBase.delay()
				return redirect("/PS2/psd/upload_progress/"+str(task.id)+"/0")

			return render(request, 'PS2/psd.html')
