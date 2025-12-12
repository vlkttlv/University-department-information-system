from django.contrib import admin
from .models import Classroom, Discipline, AdditionalWorkType, Teacher, TeacherAdditionalWork

class TeacherAdditionalWorkInline(admin.TabularInline):
    model = TeacherAdditionalWork
    extra = 1

@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ('room_number', 'capacity')
    search_fields = ('room_number', 'description')
    ordering = ('room_number',)

@admin.register(Discipline)
class DisciplineAdmin(admin.ModelAdmin):
    list_display = ('name', 'semester', 'hours')
    list_filter = ('semester',)
    search_fields = ('name',)
    ordering = ('semester', 'name')

@admin.register(AdditionalWorkType)
class AdditionalWorkTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'hours_per_week')
    search_fields = ('name', 'description')

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'middle_name', 'position', 'employment_type', 'rate', 'workplace')
    list_filter = ('employment_type', 'position', 'workplace')
    search_fields = ('last_name', 'first_name', 'middle_name', 'position', 'email')
    filter_horizontal = ('disciplines',)
    inlines = [TeacherAdditionalWorkInline]
    fieldsets = (
        ('Личные данные', {
            'fields': ('last_name', 'first_name', 'middle_name', 'photo')
        }),
        ('Контактная информация', {
            'fields': ('email', 'phone')
        }),
        ('Рабочие данные', {
            'fields': ('position', 'academic_degree', 'employment_date', 'employment_type', 'rate')
        }),
        ('Рабочее место', {
            'fields': ('workplace',)
        }),
        ('Дисциплины', {
            'fields': ('disciplines',)
        }),
        ('Дополнительная информация', {
            'fields': ('notes',)
        }),
    )

@admin.register(TeacherAdditionalWork)
class TeacherAdditionalWorkAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'work_type', 'start_date', 'end_date')
    list_filter = ('work_type', 'start_date')
    search_fields = ('teacher__last_name', 'teacher__first_name', 'description')
    ordering = ('-start_date',)