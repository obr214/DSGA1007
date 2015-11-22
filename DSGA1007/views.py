from django.shortcuts import render, render_to_response

__author__ = 'bulos87'


def home(request):
    return render(request, 'index.html')
