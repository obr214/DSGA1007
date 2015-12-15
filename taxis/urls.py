from django.conf.urls import url
from taxis import views

__author__ = 'bulos87'

urlpatterns = [
    url(r'^$', views.google_map, name='google_map'),
    url(r'^clusters$', views.test_coordinates, name='clusters'),
    url(r'^get_pdf$', views.get_report_file(), name='get_pdf'),
]