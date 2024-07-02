from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    File,
    UploadFile,
    Form
)
from sqlalchemy.orm import Session
import requests
from dotenv import load_dotenv

import os

from models import Base
from database import engine, get_db
from schemas import Meme,  MemeCreate
from crud import get_memes, get_meme, create_meme, delete_meme

load_dotenv()

app = FastAPI()

Base.metadata.create_all(bind=engine)

MEDIA_SERVICE_URL = os.getenv('MEDIA_SERVICE_URL')


@app.get('/memes', response_model=list[Meme])
def read_memes(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    '''
    Получаем список всем мемов.

    Args:
        skip (int): Отступ от начала ответа (default=0).

        limit (int): Количество выводимых записей (default=10).

        db (Session): Сессия базы данных SQLAlchemy.

    Returns:
        list[Meme]
    '''

    memes = get_memes(db, skip=skip, limit=limit)
    return memes


@app.get('/memes/{meme_id}', response_model=Meme)
def read_meme(meme_id: int, db: Session = Depends(get_db)):
    '''
    Получаем список всем мемов.

    Args:
        meme_id (int): Идентификатор искомого мема.
        db (Session): Сессия базы данных SQLAlchemy.

    Returns:
        list[Meme]

    Raises:
        HTTPException: Если мем с указанным ID не найден.
    '''

    meme = get_meme(db, meme_id)
    if meme is None:
        raise HTTPException(status_code=404, detail="Мем не найден")
    return meme


@app.post('/memes', response_model=Meme)
def create_meme_api(text: str = Form(...),
                    file: UploadFile = File(...),
                    db: Session = Depends(get_db)
                    ):
    '''
    Создает новый мем с указанным текстом и изображением.

    Args:
        text (str): Текст для нового мема.
        file (UploadFile): Файл изображения для нового мема.
        db (Session): Сессия базы данных SQLAlchemy.

    Returns:
        Meme: Созданный объект мема.

    Raises:
        HTTPException: Если произошла ошибка при загрузке
        изображения или при создании мема.
    '''

    response = requests.post(f'{MEDIA_SERVICE_URL}/upload/',
                             files={'file': (file.filename,
                                             file.file,
                                             file.content_type
                                             )}
                             )
    if response.status_code != 200:
        raise HTTPException(status_code=500,
                            detail="Ошибка при загрузке изображения."
                            )

    image_url = response.json().get("url")

    if not image_url:
        raise HTTPException(status_code=500,
                            detail="Ошибка при получении ссылки изображения."
                            )
    meme_create = MemeCreate(text=text, image_url=image_url)
    created_meme = create_meme(db, meme_create)
    return created_meme


@app.put('/memes/{meme_id}', response_model=Meme)
def update_meme(meme_id: int,
                text: str = Form(default=None),
                file: UploadFile = None, db: Session = Depends(get_db)
                ):
    '''
    Обновляет информацию о меме по его ID.

    Args:
        meme_id (int): Идентификатор мема для обновления.
        text (str, optional): Новый текст мема (по умолчанию None).
        file (UploadFile, optional): Новый файл изображения мема
        (по умолчанию None).
        db (Session): Сессия базы данных SQLAlchemy.

    Returns:
        Meme: Обновленный объект мема.

    Raises:
        HTTPException: Если мем с указанным ID не найден, происходят ошибки
        при загрузке изображения или при обновлении мема.
    '''

    meme = get_meme(db, meme_id)
    if meme is None:
        raise HTTPException(status_code=404, detail='Мем не найден')
    if file:
        response = requests.post(f'{MEDIA_SERVICE_URL}/upload/',
                                 files={'file': (file.filename,
                                                 file.file,
                                                 file.content_type)}
                                 )
        if response.status_code != 200:
            raise HTTPException(status_code=500,
                                detail='Ошибка при загрузке изображения.'
                                )
        image_url = response.json().get('url')
        if not image_url:
            raise HTTPException(status_code=500,
                                detail='Ошибка при получении URL изображения.'
                                )
        requests.delete(f'{MEDIA_SERVICE_URL}/delete/',
                        json={'url': meme.image_url}
                        )
        meme.image_url = image_url
    if text is not None:
        meme.text = text
    db.commit()
    db.refresh(meme)
    return meme


@app.delete('/memes/{meme_id}')
def delete_meme_api(meme_id: int, db: Session = Depends(get_db)):
    '''
    Удаляет мем по его ID.

    Args:
        meme_id (int): Идентификатор мема для удаления.
        db (Session): Сессия базы данных SQLAlchemy.

    Returns:
        dict: JSON объект с информацией об успешном удалении мема.

    Raises:
        HTTPException: Если мем с указанным ID не найден или
        происходят ошибки при удалении изображения или при
        удалении мема из базы данных.
    '''

    meme = get_meme(db, meme_id)
    if meme is None:
        raise HTTPException(status_code=404, detail='Мем не найден.')
    response = requests.delete(f'{MEDIA_SERVICE_URL}/delete/',
                               json={'url': meme.image_url}
                               )
    if response.status_code != 200:
        raise HTTPException(status_code=500,
                            detail='Ошибка при удалении изображения'
                            )
    delete_meme(db, meme_id)
    return {'detail': 'Мем удален'}
