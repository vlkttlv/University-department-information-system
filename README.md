# Информационная система кафедры университета
### Описание проекта
Система предназначена для секретаря кафедры и позволяет управлять:
- Преподавателями
- Аудиториями
- Дисциплинами
- Дополнительной работой (кураторство, практики, научная деятельность)

## Установка и запуск
### Клонирование репозитория
```bash
git clone https://github.com/vlkttlv/University-department-information-system.git
cd University-department-information-system
cd university_department
```
### Создание виртуального окружения
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```
### Установка зависимостей
```bash
pip install -r requirements.txt
```
### Настройка базы данных
```bash
python manage.py migrate
python manage.py createsuperuser
```
### Загрузка тестовых данных
```bash
python create_test_data.py
```
### Запуск сервера
```bash
python manage.py runserver
```
### Доступ к приложению
Приложение: ```http://127.0.0.1:8000/```
