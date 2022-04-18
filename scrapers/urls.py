from django.urls import path

from . import views


urlpatterns = [
    path('index/', views.index, name='index'),
    path('runfunction/', views.runfunction, name='thbook'),
]
