from django import forms
from .models import Teacher, Classroom, Discipline, AdditionalWorkType, TeacherAdditionalWork

class TeacherForm(forms.ModelForm):
    # Поля для аудитории (всегда создаем новую или редактируем существующую)
    room_number = forms.CharField(
        max_length=10, 
        required=True,
        label='Номер аудитории',
        help_text='Уникальный номер аудитории, например: "305"'
    )
    capacity = forms.IntegerField(
        min_value=1, 
        max_value=20, 
        required=True,
        label='Вместимость',
        initial=1,
        help_text='Вместимость аудитории (по умолчанию 1 - личный кабинет)'
    )
    classroom_description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2}),
        required=False,
        label='Описание аудитории',
        help_text='Краткое описание аудитории'
    )
    
    class Meta:
        model = Teacher
        fields = [
            'last_name', 'first_name', 'middle_name', 'email', 'phone',
            'position', 'academic_degree', 'employment_date', 'employment_type',
            'rate', 'disciplines', 'notes', 'photo'
        ]
        widgets = {
            'employment_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'disciplines': forms.SelectMultiple(attrs={'class': 'form-select', 'size': 5}),
        }
        labels = {
            'last_name': 'Фамилия',
            'first_name': 'Имя',
            'middle_name': 'Отчество',
            'email': 'Email',
            'phone': 'Телефон',
            'position': 'Должность',
            'academic_degree': 'Ученая степень',
            'employment_date': 'Дата приема на работу',
            'employment_type': 'Тип занятости',
            'rate': 'Ставка',
            'disciplines': 'Дисциплины (можно выбрать несколько)',
            'notes': 'Примечания',
            'photo': 'Фотография',
        }
        help_texts = {
            'disciplines': 'Удерживайте Ctrl для выбора нескольких дисциплин',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Если редактируем существующего преподавателя
        if self.instance.pk and self.instance.workplace:
            # Заполняем поля данными из существующей аудитории
            self.fields['room_number'].initial = self.instance.workplace.room_number
            self.fields['capacity'].initial = self.instance.workplace.capacity
            self.fields['classroom_description'].initial = self.instance.workplace.description
    
    def clean(self):
        cleaned_data = super().clean()
        
        room_number = cleaned_data.get('room_number')
        
        # Проверка уникальности номера аудитории
        if room_number:
            # Ищем аудиторию с таким номером
            existing_classroom = Classroom.objects.filter(
                room_number=room_number
            ).first()
            
            # Если редактируем существующего преподавателя
            if self.instance.pk and self.instance.workplace:
                # Проверяем, что другой аудитории с таким номером нет
                if (existing_classroom and 
                    existing_classroom != self.instance.workplace):
                    raise forms.ValidationError(
                        f"Аудитория с номером '{room_number}' уже существует "
                        f"(занята преподавателем: {existing_classroom.teacher_set.first()})."
                    )
            else:
                # При создании нового преподавателя
                if existing_classroom:
                    raise forms.ValidationError(
                        f"Аудитория с номером '{room_number}' уже существует "
                        f"(занята преподавателем: {existing_classroom.teacher_set.first()})."
                    )
        
        return cleaned_data
    
    def save(self, commit=True):
        teacher = super().save(commit=False)
        
        room_number = self.cleaned_data['room_number']
        capacity = self.cleaned_data['capacity']
        description = self.cleaned_data.get('classroom_description', '')
        
        # Если редактируем существующего преподавателя
        if self.instance.pk and self.instance.workplace:
            # Обновляем существующую аудиторию
            classroom = self.instance.workplace
            classroom.room_number = room_number
            classroom.capacity = capacity
            classroom.description = description
            classroom.save()
        else:
            # Создаем новую аудиторию
            classroom = Classroom.objects.create(
                room_number=room_number,
                capacity=capacity,
                description=description
            )
            teacher.workplace = classroom
        
        if commit:
            teacher.save()
            self.save_m2m()  # Сохраняем связи ManyToMany (дисциплины)
        
        return teacher

class ClassroomForm(forms.ModelForm):
    class Meta:
        model = Classroom
        fields = ['room_number', 'capacity', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'room_number': 'Номер аудитории',
            'capacity': 'Вместимость',
            'description': 'Описание',
        }
    
    def clean_room_number(self):
        room_number = self.cleaned_data.get('room_number')
        
        if room_number:
            # Проверяем, существует ли уже аудитория с таким номером
            existing_classroom = Classroom.objects.filter(
                room_number=room_number
            ).first()
            
            # Если редактируем существующую аудиторию
            if self.instance.pk:
                # Разрешаем сохранить, если это та же самая аудитория
                if existing_classroom and existing_classroom.pk != self.instance.pk:
                    raise forms.ValidationError(
                        f"Аудитория с номером '{room_number}' уже существует."
                    )
            else:
                # При создании новой - проверяем, что такой номер не существует
                if existing_classroom:
                    raise forms.ValidationError(
                        f"Аудитория с номером '{room_number}' уже существует."
                    )
        
        return room_number

class DisciplineForm(forms.ModelForm):
    class Meta:
        model = Discipline
        fields = ['name', 'semester', 'hours', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'name': 'Название дисциплины',
            'semester': 'Семестр',
            'hours': 'Количество часов',
            'description': 'Описание',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        semester = cleaned_data.get('semester')
        
        if name and semester:
            # Проверяем, существует ли уже дисциплина с таким названием в этом семестре
            existing_discipline = Discipline.objects.filter(
                name__iexact=name,
                semester=semester
            ).first()
            
            # Если редактируем существующую дисциплину
            if self.instance.pk:
                # Разрешаем сохранить, если это та же самая дисциплина
                if existing_discipline and existing_discipline.pk != self.instance.pk:
                    raise forms.ValidationError(
                        f"Дисциплина '{name}' уже существует в {semester} семестре."
                    )
            else:
                # При создании новой - проверяем, что такой комбинации нет
                if existing_discipline:
                    raise forms.ValidationError(
                        f"Дисциплина '{name}' уже существует в {semester} семестре."
                    )
        
        return cleaned_data
    

class AdditionalWorkTypeForm(forms.ModelForm):
    class Meta:
        model = AdditionalWorkType
        fields = ['name', 'description', 'hours_per_week']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'name': 'Название работы',
            'description': 'Описание',
            'hours_per_week': 'Часов в неделю',
        }

class TeacherAdditionalWorkForm(forms.ModelForm):
    class Meta:
        model = TeacherAdditionalWork
        fields = ['teacher', 'work_type', 'start_date', 'end_date', 'description']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'teacher': 'Преподаватель',
            'work_type': 'Тип работы',
            'start_date': 'Дата начала',
            'end_date': 'Дата окончания',
            'description': 'Описание',
        }

class AdditionalWorkTypeForm(forms.ModelForm):
    class Meta:
        model = AdditionalWorkType
        fields = ['name', 'description', 'hours_per_week']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'name': 'Название работы',
            'description': 'Описание',
            'hours_per_week': 'Часов в неделю',
        }
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        
        if name:
            # Проверяем, существует ли уже тип работы с таким названием
            existing_work_type = AdditionalWorkType.objects.filter(
                name__iexact=name
            ).first()
            
            # Если редактируем существующий тип
            if self.instance.pk:
                # Разрешаем сохранить, если это тот же самый тип
                if existing_work_type and existing_work_type.pk != self.instance.pk:
                    raise forms.ValidationError(
                        f"Тип работы с названием '{name}' уже существует."
                    )
            else:
                # При создании нового - проверяем, что такого названия нет
                if existing_work_type:
                    raise forms.ValidationError(
                        f"Тип работы с названием '{name}' уже существует."
                    )
        
        return name

class TeacherAdditionalWorkForm(forms.ModelForm):
    class Meta:
        model = TeacherAdditionalWork
        fields = ['teacher', 'work_type', 'start_date', 'end_date', 'description']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'teacher': 'Преподаватель',
            'work_type': 'Тип работы',
            'start_date': 'Дата начала',
            'end_date': 'Дата окончания',
            'description': 'Описание',
        }