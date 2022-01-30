from django.urls import path
from . import views

app_name = 'web'

urlpatterns = [
    path('', views.index, name='index'),
    path('books/<str:number>/', views.create_book_obj_view, name='create_book_obj_view'),
    path('upload-excel/', views.upload_file, name='index'),
    path('choose-photos/', views.choose_photos, name='choose_photos'),
]
