from django.urls import include, path
from django.conf.urls import url
import dev_page.views as VIEWS

app_name = 'dev_page'
urlpatterns =[
	path('', VIEWS.HomeView.as_view()),
	url('', include('django.contrib.auth.urls')),
	
]
