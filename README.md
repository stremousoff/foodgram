[![Main FoodGram workflow](https://github.com/stremousoff/foodgram/actions/workflows/main.yml/badge.svg)](https://github.com/stremousoff/foodgram/actions/workflows/main.yml)
---
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white) ![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray) ![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white) ![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white) 	![Gunicorn](https://img.shields.io/badge/gunicorn-%298729.svg?style=for-the-badge&logo=gunicorn&logoColor=white) ![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)

---
# Проект "Foodgram"

## Общее описание
"Foodgram" — это социальная платформа, ориентированная на кулинарию, которая позволяет пользователям делиться своими кулинарными творениями, обмениваться рецептами и получать вдохновение от других любителей еды. Это пространство для общения, обучения и творческого самовыражения для всех, кто интересуется приготовлением вкусной еды.

## Функции проекта
1. **Публикация контента:** Пользователи могут загружать фотографии своих блюд, описания рецептов и процесс приготовления. Можно также добавлять теги для облегчения поиска.
   
2. **Поиск и фильтрация:** Удобные инструменты поиска и фильтрации позволяют находить рецепты по времени приема блюд (завтрак, обед, ужин и т. д.) и другим критериям.

3. **Создание списков покупок:** Пользователи могут составлять списки необходимых ингредиентов для выбранных рецептов, что упрощает процесс приготовления.

4. **Социальные функции:** Возможность подписываться на других пользователей.

Проект разработан согласно микросервисной архитектуре на основе [Docker](https://www.docker.com/).

## Как развернуть проект локально

1. Установите [Docker Desktop](https://www.docker.com/products/docker-desktop/) согласно [инструкции](https://docs.docker.com/desktop/)

2. Клонируйте репозиторий [foodgram](https://github.com/stremousoff/foodgram) с помощью следующей команды:

```bash
git clone git@github.com:stremousoff/foodgram.git
```

3. В локальной директории проекта клонированного репозитория создайте файл `.env` и заполнить его по аналогии с файлом `.env.example`.

4. В локальной директории проекта клонированного репозитория запустите стек приложений с помощью команды:

```bash
docker compose up -d
```

5. Соберите статические данные и примените миграции с помощью команд:

```bash
docker compose exec backend python manage.py collectstatic
```
```bash
docker compose exec backend cp -r /app/collected_static/. /backend_static/static/
```
```bash
docker compose exec backend python manage.py migrate
```

6. Загрузите в базу данных начальный набор ингредиентов и тегов с помощью команды:
```bash
docker compose exec backend python manage.py upload_data
```

7. Вы можете открыть приложение в браузере по адресу [http://localhost](http://localhost) и увидеть его работающим.

- Используйте `docker ps` для вывода списка контейнеров.

- Используйте `docker compose down -v` для остановки стека приложений, удаления контейнеров и volumes.

- Используйте `docker image rm $(docker image ls --format '{{.Repository}}:{{.Tag}}' | grep '^foodgram-')` для удаления образов.

---

Проект "Foodgram": [Foodgram](https://foodgram.sytes.net/)

Документация к проекту: [ReDoc](https://foodgram.sytes.net/api/docs/)

Автор проекта: [Антон Стремоусов](https://github.com/stremousoff)