from django.conf.urls import url
from django.urls import path

from info.views import AboutView

app_name = 'info'

urlpatterns = [
    path('', AboutView.as_view(), name='about'),
]
