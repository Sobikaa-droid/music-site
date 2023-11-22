from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.UserRegisterView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', login_required(views.UserLogoutView.as_view(), login_url='users:register'), name='logout'),
    path('<slug:slug>/', views.UserDetailView.as_view(), name='user'),
    path('<slug:slug>/songs/', views.UserSongsListView.as_view(), name='user_songs'),
    path('<slug:slug>/albums/', views.UserAlbumsListView.as_view(), name='user_albums'),
    path('edit-profile/<int:pk>/', login_required(views.UserUpdateView.as_view(), login_url='users:register'), name='user_update'),
    path('delete/<int:pk>/', login_required(views.UserDeleteView.as_view(), login_url='users:register'), name='user_delete'),
    path('', views.UsersListView.as_view(), name='users'),
]
