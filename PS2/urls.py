from django.urls import include, path
from django.conf.urls import url
import PS2.views as VIEWS

app_name = 'PS2'
urlpatterns =[
	path('', VIEWS.HomeView.as_view()),
	url('', include('django.contrib.auth.urls')),
	url(r'^weeks/(?P<id>[0-9]+)$', VIEWS.Weeks.as_view()),
	path('student/', VIEWS.StudentEntryView.as_view()),
	path('redirect/', VIEWS.RedirectView.as_view()),
	path('mentor/', VIEWS.MentorEntryView.as_view()),
	path('mentor/<station>', VIEWS.Students_alloted_to_mentor.as_view()),
	path('mentor/<station>/<student>', VIEWS.Mentor_view_of_weeks.as_view()),
	path('mentor/<station>/<student>/lock/<enteryNumber>', VIEWS.Lock.as_view()),
	path('mentor/<station>/<student>/unlock/<enteryNumber>', VIEWS.UnLock.as_view()),
	path('mentor/<station>/<student>/<enteryNumber>', VIEWS.Mentor_view_of_entry.as_view()),
	path('student_profile/<hide>', VIEWS.Student_profile.as_view()),
	path('student_profile/<hide>/<student>', VIEWS.Student_profile.as_view()),
	path('mentor_profile/<hide>/<mentor>', VIEWS.Student_profile.as_view()),
	path('psd/', VIEWS.PSD.as_view()),
	path('psd/download_progress/<task_id>/<redirect_id>',VIEWS.DownloadProgress.as_view()),
	path('psd/upload_progress/<task_id>/<redirect_id>',VIEWS.UploadProgess.as_view()),
    # url(r'^(?P<task_id>[\w-]+)/$', VIEWS.PSD.post, name='task_status'),
]
