from django.urls import path
from user import views

app_name = 'user'
urlpatterns = [
    path('register/', views.register, name='register'),
    path('sendvcode/', views.get_vcode, name='get_vcode'),
    path('checkvcode/', views.check_vcode, name='check_vocode'),
    path('logincode/', views.login_code, name='login_codea'),
    path('login/', views.login, name='login'),
    path('image/', views.user_image, name='user_image'),
    path('profile/', views.user_profile, name='user_profile'),
    path('modifyprofile/', views.user_modify_profile, name='user_modify_profile'),
    path('modefiyimage/', views.user_modify_image, name='user_modify_image'),
    path('refreshuser/', views.refresh_user, name='refresh_user_in_cache'),
    path('alluser/', views.query_all_user, name='query_all_user'),
    path('refreshalluser/', views.refresh_all_user_cache, name='refresh_all_user_cache'),
    path('addpower/', views.add_power_on_user, name='add_power_on_user'),
    path('removepower/', views.remove_power_on_user, name='remove_power_on_user'),
    path('queryuser/', views.query_user, name='query_user'),
    path('removeuser/', views.remove_user, name='remove_user'),
    path('logout/', views.logout, name='logout'),
    path('reset/', views.reset_user_password, name='reset_user_password'),
    path('changepassword/', views.change_password, name='change_password')
]
