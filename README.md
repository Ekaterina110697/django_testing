### Тестирование проектов YaNote и YaNews

YaNews: новостной сайт, где пользователи могут оставлять комментарии к новостям.

YaNote: электронная записная книжка для тех, кто не хочет ничего забыть и поэтому всё записывает. 

# Использованные технологии:
- Python 
- Django
- Pytest
- Unittest

# Как запустить проект:
Клонировать репозиторий и перейти в него в командной строке:
```
git clone git@github.com:Ekaterina110697/django_testing.git
```

Cоздать и активировать виртуальное окружение:

```
python -m venv env
```

```
source venv\Scripts\activate  
```

Установить зависимости из файла requirements.txt:

```
python -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```
## Как запустить тесты

Переходим в директорию ya_news и запускаем Pytest:

```
cd ya_news

pytest
```

Переходим в директорию ya_note и запускаем тесты Unittest:

```
cd ya_note

python manage.py test
