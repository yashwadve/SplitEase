from django.urls import path

from . import views

app_name = "groups"

urlpatterns = [
    path('', views.group_list, name='group_list'),
    path('create/', views.group_create, name='group_create'),
    path('<int:pk>/', views.group_detail, name='group_detail'),
    path('<int:pk>/edit/', views.group_edit, name='group_edit'),
    path('<int:pk>/delete/', views.group_delete, name='group_delete'),
    path('<int:pk>/members/add/', views.add_member, name='add_member'),
    path('<int:pk>/members/<int:user_id>/remove/', views.remove_member, name='remove_member'),
]