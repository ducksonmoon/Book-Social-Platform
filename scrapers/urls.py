from django.urls import path

from . import views


urlpatterns = [
    path('index/', views.index, name='index'),
    path('thbook/', views.thbook, name='thbook'),
]
