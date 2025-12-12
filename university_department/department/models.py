from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Classroom(models.Model):
    """Аудитория"""
    room_number = models.CharField(max_length=10, verbose_name="Номер аудитории", unique=True)
    capacity = models.IntegerField(verbose_name="Вместимость", default=25)
    description = models.TextField(verbose_name="Описание", blank=True)
    
    class Meta:
        verbose_name = "Аудитория"
        verbose_name_plural = "Аудитории"
        ordering = ['room_number']
    
    def __str__(self):
        return f"Ауд. {self.room_number}"


class Discipline(models.Model):
    """Дисциплина"""
    name = models.CharField(max_length=200, verbose_name="Название дисциплины")
    semester = models.IntegerField(
        verbose_name="Семестр",
        validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    hours = models.IntegerField(verbose_name="Количество часов")
    description = models.TextField(verbose_name="Описание", blank=True)
    
    class Meta:
        verbose_name = "Дисциплина"
        verbose_name_plural = "Дисциплины"
        ordering = ['semester', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.semester} семестр)"


class AdditionalWorkType(models.Model):
    """Тип дополнительной работы"""
    name = models.CharField(max_length=100, verbose_name="Название работы")
    description = models.TextField(verbose_name="Описание", blank=True)
    hours_per_week = models.IntegerField(verbose_name="Часов в неделю", default=2)
    
    class Meta:
        verbose_name = "Тип дополнительной работы"
        verbose_name_plural = "Типы дополнительных работ"
    
    def __str__(self):
        return self.name


class Teacher(models.Model):
    """Преподаватель"""
    # Личные данные
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    middle_name = models.CharField(max_length=100, verbose_name="Отчество", blank=True)
    
    # Контактная информация
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    
    # Рабочие данные
    position = models.CharField(max_length=100, verbose_name="Должность")
    academic_degree = models.CharField(max_length=100, verbose_name="Ученая степень", blank=True)
    employment_date = models.DateField(verbose_name="Дата приема на работу")
    
    # Ставка
    FULL_TIME = 'full'
    PART_TIME = 'part'
    EMPLOYMENT_CHOICES = [
        (FULL_TIME, 'Полная ставка'),
        (PART_TIME, 'Неполная ставка'),
    ]
    employment_type = models.CharField(
        max_length=10,
        choices=EMPLOYMENT_CHOICES,
        default=FULL_TIME,
        verbose_name="Тип занятости"
    )
    rate = models.FloatField(
        verbose_name="Ставка",
        validators=[MinValueValidator(0.1), MaxValueValidator(1.0)],
        default=1.0
    )
    
    # Рабочее место
    workplace = models.ForeignKey(
        Classroom,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Рабочее место",
        unique=True
    )
    
    # Связи с другими моделями
    disciplines = models.ManyToManyField(Discipline, verbose_name="Дисциплины", blank=True)
    additional_works = models.ManyToManyField(
        AdditionalWorkType,
        through='TeacherAdditionalWork',
        verbose_name="Дополнительные работы",
        blank=True
    )
    
    # Дополнительная информация
    notes = models.TextField(verbose_name="Примечания", blank=True)
    photo = models.ImageField(upload_to='teachers/', verbose_name="Фотография", blank=True, null=True)
    
    class Meta:
        verbose_name = "Преподаватель"
        verbose_name_plural = "Преподаватели"
        ordering = ['last_name', 'first_name']
    
    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.middle_name}".strip()
    
    def full_name(self):
        return f"{self.last_name} {self.first_name} {self.middle_name}".strip()
    
    def get_employment_type_display_name(self):
        return dict(self.EMPLOYMENT_CHOICES)[self.employment_type]


class TeacherAdditionalWork(models.Model):
    """Промежуточная модель для учета дополнительной работы преподавателей"""
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name="Преподаватель")
    work_type = models.ForeignKey(AdditionalWorkType, on_delete=models.CASCADE, verbose_name="Тип работы")
    start_date = models.DateField(verbose_name="Дата начала")
    end_date = models.DateField(verbose_name="Дата окончания", null=True, blank=True)
    description = models.TextField(verbose_name="Описание", blank=True)
    
    class Meta:
        verbose_name = "Дополнительная работа преподавателя"
        verbose_name_plural = "Дополнительные работы преподавателей"
        unique_together = ['teacher', 'work_type']
    
    def __str__(self):
        return f"{self.teacher} - {self.work_type}"
