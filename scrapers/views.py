from . import thbook

from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    thbook.main()
    return HttpResponse("Hello, world. You're at the polls index.")