from django.shortcuts import render
from django.db.models import Q, Count, Sum
from .models import Teacher, Classroom, Discipline, TeacherAdditionalWork
from django.views.generic import ListView, DetailView


def home(request):
    """Главная страница"""
    context = {
        'total_teachers': Teacher.objects.count(),
        'full_time_teachers': Teacher.objects.filter(employment_type='full').count(),
        'part_time_teachers': Teacher.objects.filter(employment_type='part').count(),
        'total_classrooms': Classroom.objects.count(),
        'total_disciplines': Discipline.objects.count(),
    }
    return render(request, 'department/home.html', context)


class TeacherListView(ListView):
    """Список преподавателей"""
    model = Teacher
    template_name = 'department/teacher_list.html'
    context_object_name = 'teachers'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Teacher.objects.all().order_by('last_name', 'first_name')
        
        # Фильтрация по типу занятости
        employment_type = self.request.GET.get('employment_type')
        if employment_type:
            queryset = queryset.filter(employment_type=employment_type)
        
        # Поиск по имени
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(last_name__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(middle_name__icontains=search_query) |
                Q(position__icontains=search_query)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_count'] = Teacher.objects.count()
        context['full_time_count'] = Teacher.objects.filter(employment_type='full').count()
        context['part_time_count'] = Teacher.objects.filter(employment_type='part').count()
        return context


class TeacherDetailView(DetailView):
    """Детальная информация о преподавателе"""
    model = Teacher
    template_name = 'department/teacher_detail.html'
    context_object_name = 'teacher'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['additional_works'] = TeacherAdditionalWork.objects.filter(
            teacher=self.object
        ).select_related('work_type')
        return context


class ClassroomListView(ListView):
    """Список аудиторий"""
    model = Classroom
    template_name = 'department/classroom_list.html'
    context_object_name = 'classrooms'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Classroom.objects.annotate(
            teacher_count=Count('teacher')
        ).order_by('room_number', )

        # Поиск по номеру аудитории
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(room_number__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем общую статистику
        classrooms = self.get_queryset()
        total_capacity = sum(classroom.capacity for classroom in classrooms)
        total_teachers = sum(classroom.teacher_count for classroom in classrooms)
        
        context['total_capacity'] = total_capacity
        context['total_teachers'] = total_teachers
        return context


class ClassroomDetailView(DetailView):
    """Детальная информация об аудитории"""
    model = Classroom
    template_name = 'department/classroom_detail.html'
    context_object_name = 'classroom'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['teachers'] = Teacher.objects.filter(workplace=self.object)
        return context


class DisciplineListView(ListView):
    """Список дисциплин"""
    model = Discipline
    template_name = 'department/discipline_list.html'
    context_object_name = 'disciplines'
    ordering = ['semester', 'name']
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Фильтрация по семестру
        semester = self.request.GET.get('semester')
        if semester:
            queryset = queryset.filter(semester=semester)
        
        # Поиск по названию
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Общая статистика
        queryset = self.get_queryset()
        total_hours = sum(d.hours for d in queryset)
        total_teachers = sum(d.teacher_set.count() for d in queryset)
        
        context['total_hours'] = total_hours
        context['total_teachers'] = total_teachers
        return context


class DisciplineDetailView(DetailView):
    """Детальная информация о дисциплине"""
    model = Discipline
    template_name = 'department/discipline_detail.html'
    context_object_name = 'discipline'


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import TeacherForm, ClassroomForm, DisciplineForm, AdditionalWorkTypeForm, TeacherAdditionalWorkForm
from .models import Teacher, Classroom, Discipline, AdditionalWorkType, TeacherAdditionalWork

# Управление преподавателями
def teacher_create(request):
    if request.method == 'POST':
        form = TeacherForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Преподаватель успешно добавлен!')
            return redirect('department:teacher_list')
    else:
        form = TeacherForm()
    
    return render(request, 'department/teacher_form.html', {
        'form': form,
        'title': 'Добавление преподавателя',
        'action_url': 'department:teacher_create',
    })

def teacher_update(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    
    if request.method == 'POST':
        form = TeacherForm(request.POST, request.FILES, instance=teacher)
        if form.is_valid():
            form.save()
            messages.success(request, 'Данные преподавателя обновлены!')
            return redirect('department:teacher_detail', pk=pk)
    else:
        form = TeacherForm(instance=teacher)
    
    return render(request, 'department/teacher_form.html', {
        'form': form,
        'title': 'Редактирование преподавателя',
        'action_url': 'department:teacher_update',
        'pk': pk,
    })

def teacher_delete(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    
    if request.method == 'POST':
        teacher.delete()
        messages.success(request, 'Преподаватель удален!')
        return redirect('department:teacher_list')
    
    return render(request, 'department/teacher_confirm_delete.html', {
        'teacher': teacher,
    })


# Управление аудиториями
def classroom_create(request):
    if request.method == 'POST':
        form = ClassroomForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Аудитория успешно добавлена!')
            return redirect('department:classroom_list')
    else:
        form = ClassroomForm()
    
    return render(request, 'department/classroom_form.html', {
        'form': form,
        'title': 'Добавление аудитории',
        'action_url': 'department:classroom_create',
    })

def classroom_update(request, pk):
    classroom = get_object_or_404(Classroom, pk=pk)
    
    if request.method == 'POST':
        form = ClassroomForm(request.POST, instance=classroom)
        if form.is_valid():
            form.save()
            messages.success(request, 'Данные аудитории обновлены!')
            return redirect('department:classroom_detail', pk=pk)
    else:
        form = ClassroomForm(instance=classroom)
    
    return render(request, 'department/classroom_form.html', {
        'form': form,
        'title': 'Редактирование аудитории',
        'action_url': 'department:classroom_update',
        'pk': pk,
    })

def classroom_delete(request, pk):
    classroom = get_object_or_404(Classroom, pk=pk)
    
    if request.method == 'POST':
        classroom.delete()
        messages.success(request, 'Аудитория удалена!')
        return redirect('department:classroom_list')
    
    return render(request, 'department/classroom_confirm_delete.html', {
        'classroom': classroom,
    })

# Управление дисциплинами
def discipline_create(request):
    if request.method == 'POST':
        form = DisciplineForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Дисциплина успешно добавлена!')
            return redirect('department:discipline_list')
    else:
        form = DisciplineForm()
    
    return render(request, 'department/discipline_form.html', {
        'form': form,
        'title': 'Добавление дисциплины',
        'action_url': 'department:discipline_create',
    })

def discipline_update(request, pk):
    discipline = get_object_or_404(Discipline, pk=pk)
    
    if request.method == 'POST':
        form = DisciplineForm(request.POST, instance=discipline)
        if form.is_valid():
            form.save()
            messages.success(request, 'Данные дисциплины обновлены!')
            return redirect('department:discipline_detail', pk=pk)
    else:
        form = DisciplineForm(instance=discipline)
    
    return render(request, 'department/discipline_form.html', {
        'form': form,
        'title': 'Редактирование дисциплины',
        'action_url': 'department:discipline_update',
        'pk': pk,
    })

def discipline_delete(request, pk):
    discipline = get_object_or_404(Discipline, pk=pk)
    
    if request.method == 'POST':
        discipline.delete()
        messages.success(request, 'Дисциплина удалена!')
        return redirect('department:discipline_list')
    
    return render(request, 'department/discipline_confirm_delete.html', {
        'discipline': discipline,
    })

# Управление типами дополнительной работы
def additional_work_type_create(request):
    if request.method == 'POST':
        form = AdditionalWorkTypeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Тип дополнительной работы добавлен!')
            return redirect('department:additional_work_type_list')
    else:
        form = AdditionalWorkTypeForm()
    
    return render(request, 'department/additional_work_type_form.html', {
        'form': form,
        'title': 'Добавление типа дополнительной работы',
        'action_url': 'department:additional_work_type_create',
    })

def additional_work_type_list(request):
    work_types = AdditionalWorkType.objects.all()
    return render(request, 'department/additional_work_type_list.html', {
        'work_types': work_types,
    })

def additional_work_type_update(request, pk):
    work_type = get_object_or_404(AdditionalWorkType, pk=pk)
    
    if request.method == 'POST':
        form = AdditionalWorkTypeForm(request.POST, instance=work_type)
        if form.is_valid():
            form.save()
            messages.success(request, 'Тип дополнительной работы обновлен!')
            return redirect('department:additional_work_type_list')
    else:
        form = AdditionalWorkTypeForm(instance=work_type)
    
    return render(request, 'department/additional_work_type_form.html', {
        'form': form,
        'title': 'Редактирование типа дополнительной работы',
        'action_url': 'department:additional_work_type_update',
        'pk': pk,
    })

def additional_work_type_delete(request, pk):
    work_type = get_object_or_404(AdditionalWorkType, pk=pk)
    
    if request.method == 'POST':
        work_type.delete()
        messages.success(request, 'Тип дополнительной работы удален!')
        return redirect('department:additional_work_type_list')
    
    return render(request, 'department/additional_work_type_confirm_delete.html', {
        'work_type': work_type,
    })

# Назначение дополнительной работы преподавателям
def teacher_additional_work_create(request):
    if request.method == 'POST':
        form = TeacherAdditionalWorkForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Дополнительная работа назначена!')
            return redirect('department:teacher_additional_work_list')
    else:
        form = TeacherAdditionalWorkForm()
    
    return render(request, 'department/teacher_additional_work_form.html', {
        'form': form,
        'title': 'Назначение дополнительной работы',
        'action_url': 'department:teacher_additional_work_create',
    })

def teacher_additional_work_list(request):
    additional_works = TeacherAdditionalWork.objects.all().select_related('teacher', 'work_type')
    return render(request, 'department/teacher_additional_work_list.html', {
        'additional_works': additional_works,
    })

def teacher_additional_work_update(request, pk):
    additional_work = get_object_or_404(TeacherAdditionalWork, pk=pk)
    
    if request.method == 'POST':
        form = TeacherAdditionalWorkForm(request.POST, instance=additional_work)
        if form.is_valid():
            form.save()
            messages.success(request, 'Дополнительная работа обновлена!')
            return redirect('department:teacher_additional_work_list')
    else:
        form = TeacherAdditionalWorkForm(instance=additional_work)
    
    return render(request, 'department/teacher_additional_work_form.html', {
        'form': form,
        'title': 'Редактирование дополнительной работы',
        'action_url': 'department:teacher_additional_work_update',
        'pk': pk,
    })

def teacher_additional_work_delete(request, pk):
    additional_work = get_object_or_404(TeacherAdditionalWork, pk=pk)
    
    if request.method == 'POST':
        additional_work.delete()
        messages.success(request, 'Дополнительная работа удалена!')
        return redirect('department:teacher_additional_work_list')
    
    return render(request, 'department/teacher_additional_work_confirm_delete.html', {
        'additional_work': additional_work,
    })