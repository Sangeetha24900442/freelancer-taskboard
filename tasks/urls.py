from django.urls import path
from . import views

urlpatterns = [
    path('', views.task_list, name='task_list'),
    path('add/', views.add_task, name='add_task'),
    path('edit/<int:pk>/', views.edit_task, name='edit_task'),
    path('delete/<int:pk>/', views.delete_task, name='delete_task'),
    path('task/<int:task_id>/apply/', views.apply_to_task, name='apply_to_task'),
    path('task/<int:task_id>/confirm/<int:applicant_id>/', views.mark_in_progress, name='mark_in_progress'),


]
