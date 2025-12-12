from django.urls import path
from . import views

app_name = 'department'

urlpatterns = [
    path('', views.home, name='home'),
    # Преподаватели
    path('teachers/', views.TeacherListView.as_view(), name='teacher_list'),
    path('teachers/<int:pk>/', views.TeacherDetailView.as_view(), name='teacher_detail'),
    path('teachers/add/', views.teacher_create, name='teacher_create'),
    path('teachers/<int:pk>/edit/', views.teacher_update, name='teacher_update'),
    path('teachers/<int:pk>/delete/', views.teacher_delete, name='teacher_delete'),
    
    # Аудитории
    path('classrooms/', views.ClassroomListView.as_view(), name='classroom_list'),
    path('classrooms/<int:pk>/', views.ClassroomDetailView.as_view(), name='classroom_detail'),
    path('classrooms/add/', views.classroom_create, name='classroom_create'),
    path('classrooms/<int:pk>/edit/', views.classroom_update, name='classroom_update'),
    path('classrooms/<int:pk>/delete/', views.classroom_delete, name='classroom_delete'),
    
    # Дисциплины
    path('disciplines/', views.DisciplineListView.as_view(), name='discipline_list'),
    path('disciplines/<int:pk>/', views.DisciplineDetailView.as_view(), name='discipline_detail'),
    path('disciplines/add/', views.discipline_create, name='discipline_create'),
    path('disciplines/<int:pk>/edit/', views.discipline_update, name='discipline_update'),
    path('disciplines/<int:pk>/delete/', views.discipline_delete, name='discipline_delete'),
    
    # Типы дополнительной работы
    path('additional-work-types/', views.additional_work_type_list, name='additional_work_type_list'),
    path('additional-work-types/add/', views.additional_work_type_create, name='additional_work_type_create'),
    path('additional-work-types/<int:pk>/edit/', views.additional_work_type_update, name='additional_work_type_update'),
    path('additional-work-types/<int:pk>/delete/', views.additional_work_type_delete, name='additional_work_type_delete'),
    
    # Назначение дополнительной работы
    path('teacher-additional-works/', views.teacher_additional_work_list, name='teacher_additional_work_list'),
    path('teacher-additional-works/add/', views.teacher_additional_work_create, name='teacher_additional_work_create'),
    path('teacher-additional-works/<int:pk>/edit/', views.teacher_additional_work_update, name='teacher_additional_work_update'),
    path('teacher-additional-works/<int:pk>/delete/', views.teacher_additional_work_delete, name='teacher_additional_work_delete'),

]