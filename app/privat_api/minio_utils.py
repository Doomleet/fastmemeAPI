from minio import Minio
from minio.error import S3Error
import os
from dotenv import load_dotenv


load_dotenv()
MINIO_ENDPOINT_URL = os.getenv('MINIO_ENDPOINT_URL')
MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY')
MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY')
MINIO_BUCKET_NAME = os.getenv('MINIO_BUCKET_NAME')
IMG_DOWNLOAD_ENDPOINT_URL = os.getenv('IMG_DOWNLOAD_ENDPOINT_URL')


minio_client = Minio(
    MINIO_ENDPOINT_URL,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)

if not minio_client.bucket_exists(MINIO_BUCKET_NAME):
    minio_client.make_bucket(MINIO_BUCKET_NAME)


def upload_file(file_name, bucket, object_name=None):
    '''
    Загрузка файла в указанный бакет
    '''

    if object_name is None:
        object_name = file_name
    minio_client.fput_object(bucket, object_name, file_name)


def get_file_url(bucket, object_name):
    '''
    Получение URL файла
    '''

    return f'http://{IMG_DOWNLOAD_ENDPOINT_URL}/{bucket}/{object_name}'


def delete_file(bucket, object_name):
    '''
    Удаление файла из бакета
    '''
    minio_client.remove_object(bucket, object_name)


def file_exists(bucket, object_name):
    '''
    Проверка существования файла в бакете
    '''

    try:
        minio_client.stat_object(bucket, object_name)
        return True
    except S3Error:
        return False


def get_unique_filename(bucket_name, original_filename):
    base, extension = os.path.splitext(original_filename)
    index = 1
    new_filename = original_filename
    while file_exists(bucket_name, new_filename):
        new_filename = f'{base}_{index}{extension}'
        index += 1
    return new_filename
