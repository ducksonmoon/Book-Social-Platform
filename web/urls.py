from django.urls import path
from . import views

app_name = 'web'

urlpatterns = [
    path('upload-excel/', views.upload_file, name='index'),
    path('choose-photos/', views.choose_photos, name='choose_photos'),
]
