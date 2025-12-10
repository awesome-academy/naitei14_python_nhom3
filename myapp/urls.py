from django.urls import path
from . import views

app_name = 'myapp'

urlpatterns = [
    path('', views.index, name='index'),
    path('detail/', views.detail, name='detail'),
    
    # Auth URLs
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('profile/', views.render_profile_page, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    
    # Email verification & Password reset
    path('activate/<str:token>/', views.activate_account, name='activate_account'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<str:token>/', views.reset_password, name='reset_password'),
]
