from django.urls import path

from . import views

app_name = "expenses"

urlpatterns = [
    path('group/<int:group_id>/add/', views.expense_create, name='expense_create'),
    path('<int:pk>/', views.expense_detail, name='expense_detail'),
    path('<int:pk>/edit/', views.expense_edit, name='expense_edit'),
    path('<int:pk>/delete/', views.expense_delete, name='expense_delete'),
]