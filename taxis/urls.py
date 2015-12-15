from django.conf.urls import url
from taxis import views

__author__ = 'bulos87'

urlpatterns = [
    url(r'^$', views.pick_ups, name='pick_ups'),
    url(r'^get_pdf$', views.get_report_file, name='get_pdf'),
]