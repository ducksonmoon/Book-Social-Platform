from django.urls import path

from accounts.views import ProfileView, ProfileBookListView


urlpatterns = [
    path('profile/<str:username>/', ProfileView.as_view(), name='profile'),
    path('profile/<str:username>/books/<str:list>/', ProfileBookListView.as_view(), name='profile-books-read-later'),
    # Follow and Unfollow
    path('action/<str:username>/', ProfileView.as_view(), name='follow'),
]
