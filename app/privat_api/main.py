from fastapi import FastAPI, File, UploadFile, HTTPException
from minio_utils import (
    upload_file,
    get_file_url,
    delete_file,
    get_unique_filename
)
import os
from schemas import DeleteMemeRequest
from dotenv import load_dotenv


load_dotenv()

app = FastAPI()

BUCKET_NAME = os.getenv('MINIO_BUCKET_NAME')
TMP_DIR = os.getenv('TMP_DIR')


@app.post('/upload/')
async def upload_meme_image(file: UploadFile = File(...)):
    '''
    Загружает изображение мема в хранилище.

    Args:
        file (UploadFile): Файл изображения мема.

    Returns:
        dict: JSON объект с URL загруженного изображения.

    Raises:
        HTTPException: Если происходят ошибки при загрузке файла во
        временную директорию, при загрузке файла в хранилище,
        или при получении URL файла.
    '''

    try:
        os.makedirs(TMP_DIR, exist_ok=True)
        file_location = os.path.join(TMP_DIR, file.filename)
        with open(file_location, 'wb+') as file_object:
            file_object.write(file.file.read())
        unique_filename = get_unique_filename(BUCKET_NAME, file.filename)
        upload_file(file_location, BUCKET_NAME, unique_filename)
        os.remove(file_location)
        url = get_file_url(BUCKET_NAME, unique_filename)
        return {'url': url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete('/delete/')
async def delete_meme_image(request: DeleteMemeRequest):
    '''
    Удаляет изображение мема из хранилища.

    Args:
        request (DeleteMemeRequest): Объект запроса с URL изображения мема.

    Returns:
        dict: JSON объект с информацией об успешном удалении изображения.

    Raises:
        HTTPException: Если происходят ошибки при удалении файла из хранилища.
    '''

    try:
        object_name = request.url.split('/')[-1]
        delete_file(BUCKET_NAME, object_name)
        return {'detail': 'Изображение удалено'}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
