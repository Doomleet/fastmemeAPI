# fastmemedb


Использованные технологии:
* Веб-фреймворк: FastAPI
* База данных: minio + postgreSQL
* Контейнеризация: docker

Расположение .env
```
└── app/                  
    └── api/
        ├── ...
        ├── .env            
    └── privat_api 
        ├── ... 
        ├── .env                 
├── ... 
├── docker-compose.yml
├── .env
```

Формат app/api/.env:
``` 
MEDIA_SERVICE_URL="http://privat_api:80/"
DB_USERNAME="admin"
DB_PASSWORD="qasaq123"
DB_NAME="memes"
DB_STATUS="postgres"

TEST_DB_USERNAME="test_user"
TEST_DB_PASSWORD="test_password"
TEST_DB_STATUS="test_postgres"
TEST_DB_NAME="test_db"
```

Формат app/privat_api/.env:
``` 
MINIO_ENDPOINT_URL = 'minio:9000'
MINIO_ACCESS_KEY = 'minioadmin'
MINIO_SECRET_KEY = 'minioadmin'
MINIO_BUCKET_NAME = 'memes'
IMG_DOWNLOAD_ENDPOINT_URL = 'localhost:9000'
TMP_DIR = "/tmp"
```

Формат .env (для docker-compose):
```
DB_USER=admin
DB_PASSWORD=qasaq123
DB_NAME=memes
```

Запуск backend'а:
```
docker compose -f docker-compose.yml up --build
```

Для корректной работы публичного хранилища в контейнере minio (режим раздачи для анонимных юзеров):

```
docker compose -f docker-compose.yml exec minio mc alias set myminio http://minio:9000 minioadmin minioadmin
docker compose -f docker-compose.yml exec minio mc anonymous get myminio/memes
docker compose -f docker-compose.yml exec minio  mc anonymous set download myminio/memes
```


Запуск тестов
```
docker compose -f docker-compose.yml up --build
docker compose -f docker-compose.yml exec public_api pytest
```

### GET /memes
Получить список всех мемов.

**Параметры:**
- `skip` (int, необязательно): Отступ от начала списка. По умолчанию 0.
- `limit` (int, необязательно): Количество элементов для получения. По умолчанию 10.

**Ответы:**
- 200: Список мемов.

### GET /memes/{meme_id}
Получить конкретный мем по его ID.

**Параметры:**
- `meme_id` (int): ID мема для получения.

**Ответы:**
- 200: Запрашиваемый мем.
- 404: Мем не найден.

### POST /memes
Создать новый мем с указанным текстом и изображением.

**Параметры:**
- `text` (str): Текст для нового мема.
- `file` (UploadFile): Файл изображения для нового мема.

**Ответы:**
- 200: Созданный объект мема.
- 422: Ошибка при заполнении body.
- 500: Ошибка при загрузке изображения или при создании мема.

### PUT /memes/{meme_id}
Обновить информацию о меме по его ID.

**Параметры:**
- `meme_id` (int): ID мема для обновления.
- `text` (str, необязательно): Новый текст мема (по умолчанию None).
- `file` (UploadFile, необязательно): Новый файл изображения мема (по умолчанию None).

**Ответы:**
- 200: Обновленный объект мема.
- 404: Мем не найден.
- 422: Ошибка при заполнении body.
- 500: Ошибка при загрузке изображения или при обновлении мема.

### DELETE /memes/{meme_id}
Удалить мем по его ID.

**Параметры:**
- `meme_id` (int): ID мема для удаления.

**Ответы:**
- 200: JSON объект с информацией об успешном удалении мема.
- 404: Мем не найден.
- 500: Ошибка при удалении изображения или мема из базы данных.