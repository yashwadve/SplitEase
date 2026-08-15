from django.urls import path

from . import views

app_name = "settlements"

urlpatterns = [
    path('group/<int:group_id>/', views.balance_sheet, name='balance_sheet'),
    path('group/<int:group_id>/record/', views.record_settlement, name='record'),
    path('group/<int:group_id>/history/', views.settlement_history, name='history'),
    path('<int:pk>/complete/', views.mark_settlement_completed, name='complete'),
]