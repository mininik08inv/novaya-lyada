Для работы приложения необходимо:

1.Поднимите Redis (локально): 
docker run -d --name redis -p 6379:6379 redis:7

2) Запустите Celery worker и beat в отдельных терминалах из корня проекта:
# worker
uv run celery -A nl_website worker -l info

# beat (планировщик)
uv run celery -A nl_website beat -l info