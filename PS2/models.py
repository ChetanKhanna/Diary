from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class UserIdPassword(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	token = models.IntegerField(default=0)


class Mentor(models.Model):
	mentor_id = models.CharField(max_length=10, primary_key=True, unique=True)
	mentor_name = models.CharField(max_length=45)
	mentor_contact = models.CharField(max_length=40)
	mentor_email = models.EmailField()

	def __str__(self):
		return str(self.mentor_id)


class Station(models.Model):
	mentor = models.ForeignKey(Mentor, on_delete=models.CASCADE)
	station_name = models.CharField(max_length=100, primary_key=True, unique=True)
	station_address = models.CharField(max_length=200)

	def __str__(self):
		return str(self.station_name)


class Student(models.Model):
	station = models.ForeignKey(Station, on_delete=models.CASCADE)
	student_id = models.CharField(max_length=13, primary_key=True,unique=True)
	student_name = models.CharField(max_length=45)
	student_contact = models.CharField(max_length=40)
	student_email = models.EmailField()
	check=models.CharField(max_length=2000)

	organization_mentor = models.CharField(max_length=50)
	organization_email_id = models.EmailField()
	organization_contact = models.CharField(max_length=50)

	def __str__(self):
		return str(self.student_id)


class Week(models.Model):
	week_no = models.IntegerField(default=0)
	user_id = models.ForeignKey(Student, on_delete=models.CASCADE)
	tasksplanned = models.CharField(max_length=2500, default="")
	taskscompleted = models.CharField(max_length=2500, default="")
	variation = models.CharField(max_length=2500, default="")
	nextweek = models.CharField(max_length=2500, default="")
	learning = models.CharField(max_length=2500, default="")
	equipments = models.CharField(max_length=2500, default="")
	comment = models.CharField(max_length=2500, default="")
	lock = models.IntegerField(default=0)
	# lock==1 means locked else unlocked
	submissionDate = models.DateTimeField()

	class Meta:
		unique_together = (('week_no', 'user_id'),)

	def __str__(self):
		return str((self.user_id,self.week_no))
