from django.urls import path
from patch import views

app_name = 'patch'
urlpatterns = [
    path('add/', views.add_patch, name='add_patch'),
    path('delete/', views.delete_patch, name='delete_patch'),
    path('query/', views.query_all_patch, name='query_all_patch'),
    path('modify/', views.modify_patch, name='modify_patch'),
    path('refresh/', views.refresh_patch, name='refresh_patch')
]
