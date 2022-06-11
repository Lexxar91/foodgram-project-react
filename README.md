# Foodgram - продуктовый помощник
 
## Проект находится по адресу: http://130.193.42.133/

## Стек технологий
[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat-square&logo=Django)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat-square&logo=Django%20REST%20Framework)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat-square&logo=PostgreSQL)](https://www.postgresql.org/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat-square&logo=NGINX)](https://nginx.org/ru/)
[![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat-square&logo=gunicorn)](https://gunicorn.org/)
[![docker](https://img.shields.io/badge/-Docker-464646?style=flat-square&logo=docker)](https://www.docker.com/)
[![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat-square&logo=GitHub%20actions)](https://github.com/features/actions)

## Описание проекта
Онлайн-сервис Foodgram («Продуктовый помощник») создан для начинающих кулинаров и опытных гурманов. В сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать в формате .txt сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

Проект разворачивается в Docker контейнерах: backend-приложение API, PostgreSQL-база данных, nginx-сервер и frontend-контейнер.

Реализовано CI и CD проекта. При пуше изменений в главную ветку проект автоматические тестируется на соотвествие требованиям PEP8. После успешного прохождения тестов, на git-платформе собирается образ backend-контейнера Docker и автоматически размещается в облачном хранилище DockerHub. Размещенный образ автоматически разворачивается на боевом сервере вмете с контейнером веб-сервера nginx и базой данных PostgreSQL.

## Системные требования
- Python 3.7+
- Docker
- Works on Linux, Windows, macOS

## Запуск проекта в контейнере
Клонируйте репозиторий и перейдите в него в командной строке.
Создайте и активируйте виртуальное окружение:
```
https://github.com/Lexxar91/foodgram-project-react
cd foodgram-project-react
```
Должен быть свободен порт 8000. PostgreSQL поднимается на 5432 порту, он тоже должен быть свободен.
Cоздать и открыть файл .env с переменными окружения:
```
cd infra
touch .env
```
Заполнить .env файл с переменными окружения: 
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
DB_HOST=db
DB_PORT=5432
```
Установить и запустить приложения в контейнерах (образ для контейнера web загружается из DockerHub):
```
docker-compose up -d
```
Запустить миграции, создать суперюзера, собрать статику и заполнить а БД таблицы с ингредиентами и тегами:
```
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python manage.py collectstatic --no-input 
docker-compose exec backend python manage.py importcsvdata
docker-compose exec backend python manage.py importtags
```