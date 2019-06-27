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
from zipfile import ZipFile
from threading import Thread
import time
import os
# importing models of PS2
# from . models import Student, Station, Mentor, Week, UserIdPassword
# importing tasks of PS2
# from dev_page.tasks import PopulateDataBase

## Views for PS2
class HomeView(generic.TemplateView):
	template_name = 'dev_page.html'

