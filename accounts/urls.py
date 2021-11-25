from django.urls import path

from accounts.views import ProfileView, ProfileBookListView, BookListViewSet, ProfileFollowingsView, SearchViewSet


urlpatterns = [
    path('profile/<str:username>/', ProfileView.as_view(), name='profile'),
    path('profile/<str:username>/books/<str:list>/', ProfileBookListView.as_view(), name='profile-books-read-later'),
    path('profile/<str:username>/followings/', ProfileFollowingsView.as_view({'get': 'list'}), name='profile-followings'),
    path('profile/<str:username>/lists/', BookListViewSet.as_view({'get': 'list'}), name='profile-books-read-later-page'),
    # Search username
    path('', SearchViewSet.as_view(), name='search'),
    # Follow and Unfollow
    path('action/<str:username>/', ProfileView.as_view(), name='follow'),
]
