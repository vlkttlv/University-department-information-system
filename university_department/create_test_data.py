import os
import django
from datetime import date, timedelta
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'university_department.settings')
django.setup()

from department.models import Classroom, Discipline, AdditionalWorkType, Teacher, TeacherAdditionalWork

def create_test_data():
    print("Создание тестовых данных...")
    
    # Очищаем базу данных
    TeacherAdditionalWork.objects.all().delete()
    Teacher.objects.all().delete()
    AdditionalWorkType.objects.all().delete()
    Discipline.objects.all().delete()
    Classroom.objects.all().delete()
    
    # Создаем аудитории - 25 штук
    classrooms = []
    floors = [1, 2, 3, 4, 5]  # 5 этажей
    
    for i in range(1, 26):  # 25 аудиторий
        floor = floors[(i-1) % 5]  # равномерно распределяем по этажам
        room_number = f"{floor}{str(i).zfill(2)}"  # Номер: этаж + двузначный номер
        
        classroom = Classroom.objects.create(
            room_number=room_number,
            capacity=random.randint(1, 1),  # Вместимость 1 человек (личный кабинет)
            description=f"Преподавательская аудитория №{i} ({floor} этаж)"
        )
        classrooms.append(classroom)
        print(f"Создана аудитория: {classroom}")
    
    # Перемешиваем список аудиторий для случайного распределения
    random.shuffle(classrooms)
    
    # Создаем дисциплины
    disciplines = []
    discipline_names = [
        "Введение в ИТ",
        "Интернет программирование",
        "Информатика 1.2",
        "Теория вероятностей",
        "Программирование",
        "Базы данных",
        "Операционные системы",
        "DevOps",
        "Нейронные сети и глубокое обучение",
        "Веб-разработка",
        "Математический анализ",
        "Линейная алгебра",
        "Дискретная математика",
        "Компьютерные сети",
        "Искусственный интеллект",
        "Мобильная разработка",
        "Тестирование ПО",
        "Архитектура ЭВМ",
        "Кибербезопасность"
    ]
    
    for i, name in enumerate(discipline_names, 1):
        discipline = Discipline.objects.create(
            name=name,
            semester=random.randint(1, 8),
            hours=random.randint(36, 144),
            description=f"Курс по дисциплине '{name}'"
        )
        disciplines.append(discipline)
        print(f"Создана дисциплина: {discipline}")
    
    # Создаем типы дополнительной работы
    work_types = []
    work_type_names = [
        "Кураторство",
        "Руководство УИРС",
        "Руководство НИРС",
        "Руководство ВКР",
        "Научная деятельность",
        "Методическая работа",
        "Работа в комиссиях",
        "Проведение практики",
    ]
    
    for name in work_type_names:
        work_type = AdditionalWorkType.objects.create(
            name=name,
            hours_per_week=random.randint(1, 5),
            description=f"Дополнительная работа: {name}"
        )
        work_types.append(work_type)
        print(f"Создан тип работы: {work_type}")
    
    # Создаем преподавателей - 25 человек
    last_names = ["Иванов", "Петров", "Сидоров", "Смирнов", "Кузнецов", 
                  "Попов", "Васильев", "Федоров", "Морозов", "Волков",
                  "Алексеев", "Лебедев", "Семенов", "Егоров", "Павлов",
                  "Козлова", "Степанова", "Николаева", "Орлова", "Андреева",
                  "Макарова", "Никитина", "Захарова", "Зайцева", "Соловьева"]
    
    first_names = ["Александр", "Алексей", "Андрей", "Дмитрий", "Евгений",
                   "Иван", "Максим", "Михаил", "Сергей", "Юрий",
                   "Вячеслав", "Владислав", "Виктор", "Владимир", "Константин",
                   "Светлана", "Татьяна", "Наталья", "Екатерина", "Юлия",
                   "Анна", "Ольга", "Мария", "Ирина", "Елена"]
    
    middle_names = ["Александрович", "Алексеевич", "Андреевич", "Дмитриевич", "Викторович",
                    "Евгеньевич", "Иванович", "Михайлович", "Сергеевич", "Сабитович",
                    "Вячеславович", "Геннадьевич", "Алексеевич", "Александрович", "Давидович",
                    "Евгеньевна", "Ивановна", "Михайловна", "Сергеевна", "Вячеславовна",
                    "Александровна", "Алексеевна", "Андреевна", "Дмитриевна", "Артемовна"]
    
    positions = ["Профессор", "Доцент", "Старший преподаватель", "Ассистент", "Директор", "Заведующий кафедрой"]
    
    academic_degrees = ["Доктор наук", "Кандидат технических наук", "Кандидат физико-математических наук", 
                        "Кандидат педагогических наук", ""]
    
    teachers = []
    
    for i in range(25):  # 25 преподавателей
        # Определяем тип занятости и ставку
        if i < 15:  # 15 преподавателей на полной ставке
            employment_type = 'full'
            rate = 1.0
        else:  # 10 преподавателей на неполной ставке
            employment_type = 'part'
            rate = round(random.uniform(0.25, 0.75), 2)
        
        # Уникальная аудитория для каждого преподавателя
        assigned_classroom = classrooms[i]  # Каждому - своя аудитория
        
        # Создаем преподавателя с гарантированным рабочим местом
        teacher = Teacher.objects.create(
            last_name=last_names[i],
            first_name=first_names[i],
            middle_name=middle_names[i],
            position=random.choice(positions),
            academic_degree=random.choice(academic_degrees),
            employment_date=date(2015 + i % 10, 1 + i % 11, 1 + i % 28),
            employment_type=employment_type,
            rate=rate,
            workplace=assigned_classroom,
            email=f"{last_names[i].lower()}.{first_names[i][0].lower()}@university.ru",
            phone=f"+7(9{random.randint(10, 99)})-{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(10, 99)}",
            notes=f"Преподаватель №{i+1}. " + ("Ответственный работник." if i % 5 == 0 else "")
        )
        
        # Назначаем случайные дисциплины (от 1 до 5)
        teacher_disciplines = random.sample(disciplines, random.randint(1, 5))
        teacher.disciplines.set(teacher_disciplines)
        
        # Назначаем случайные дополнительные работы (от 0 до 3)
        if random.random() > 0.3:  # 70% преподавателей имеют доп. работу
            teacher_works = random.sample(work_types, random.randint(1, 3))
            for work in teacher_works:
                TeacherAdditionalWork.objects.create(
                    teacher=teacher,
                    work_type=work,
                    start_date=date(2023, 1, 1),
                    end_date=date(2024, 6, 30) if random.random() > 0.5 else None,
                    description=f"Выполнение работы: {work.name}"
                )
        
        teachers.append(teacher)
        print(f"Создан преподаватель: {teacher} в аудитории {assigned_classroom.room_number}")
    
    # Проверяем уникальность аудиторий
    print("\n" + "="*50)
    print("ПРОВЕРКА УНИКАЛЬНОСТИ АУДИТОРИЙ:")
    print("="*50)
    
    used_classrooms = set()
    for teacher in Teacher.objects.all():
        if teacher.workplace:
            if teacher.workplace.id in used_classrooms:
                print(f"ОШИБКА: Аудитория {teacher.workplace.room_number} повторяется!")
            else:
                used_classrooms.add(teacher.workplace.id)
                print(f"✓ Преподаватель {teacher.full_name()} → Аудитория {teacher.workplace.room_number}")
    
    # Статистика
    print("\n" + "="*50)
    print("СТАТИСТИКА СОЗДАННЫХ ДАННЫХ:")
    print("="*50)
    print(f"Всего создано:")
    print(f"- Аудиторий: {Classroom.objects.count()} (все уникальные)")
    print(f"- Дисциплин: {Discipline.objects.count()}")
    print(f"- Типов доп. работ: {AdditionalWorkType.objects.count()}")
    print(f"- Преподавателей: {Teacher.objects.count()}")
    print(f"- Преподавателей с аудиториями: {Teacher.objects.filter(workplace__isnull=False).count()}")
    print(f"- Доп. работ преподавателей: {TeacherAdditionalWork.objects.count()}")
    
    # Проверка распределения по ставкам
    print(f"\nРаспределение по ставкам:")
    print(f"- Полная ставка: {Teacher.objects.filter(employment_type='full').count()}")
    print(f"- Неполная ставка: {Teacher.objects.filter(employment_type='part').count()}")
    
    # Проверка свободных аудиторий (должно быть 0)
    free_classrooms = Classroom.objects.filter(teacher__isnull=True)
    print(f"\nСвободных аудиторий: {free_classrooms.count()} (должно быть 0)")

if __name__ == "__main__":
    create_test_data()