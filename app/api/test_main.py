import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

import os

from main import app
from database import Base, get_db


load_dotenv()
TEST_DB_USERNAME = os.getenv('TEST_DB_USERNAME')
TEST_DB_PASSWORD = os.getenv('TEST_DB_PASSWORD')
TEST_DB_PORT = os.getenv('TEST_DB_PORT')
TEST_DB_NAME = os.getenv('TEST_DB_NAME')
SQLALCHEMY_TEST_DATABASE_URI = f'postgresql://{TEST_DB_USERNAME}:{TEST_DB_PASSWORD}@{TEST_DB_PORT}/{TEST_DB_NAME}'


@pytest.fixture(scope='module')
def db_engine():
    '''
    Инициализация соединения с БД.
    '''

    engine = create_engine(SQLALCHEMY_TEST_DATABASE_URI)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope='module')
def db_session(db_engine):
    '''
    Сессия БД для тестов.
    '''

    TestingSessionLocal = sessionmaker(autocommit=False,
                                       autoflush=False,
                                       bind=db_engine
                                       )
    db = TestingSessionLocal()
    yield db
    db.close()


@pytest.fixture(scope='module')
def client(db_session):
    '''
    Клиент.
    '''

    app.dependency_overrides[get_db] = lambda: db_session
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_read_memes(client):
    response = client.get('/memes')
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_meme(client):
    response = client.post(
        '/memes',
        data={'text': 'test_mem'},
        files={'file': ('test.jpg', b'content', 'image/jpeg')}
    )
    get_response = client.get('/memes/1')
    assert response.status_code == 200
    assert 'id' in response.json()
    assert response.json()['text'] == 'test_mem'
    assert get_response.status_code == 200


def test_update_meme(client):
    create_response = client.post(
        '/memes',
        data={'text': 'test_mem'},
        files={'file': ('test.jpg', b'content', 'image/jpeg')}
    )
    meme_id = create_response.json()['id']
    update_response = client.put(
        f'/memes/{meme_id}',
        data={'text': 'updated_test_mem'}
    )
    assert update_response.status_code == 200
    assert update_response.json()['text'] == 'updated_test_mem'


def test_delete_meme(client):
    create_response = client.post(
        '/memes',
        data={'text': 'test_mem'},
        files={'file': ('test.jpg', b'content', 'image/jpeg')}
    )
    meme_id = create_response.json()['id']
    delete_response = client.delete(f'/memes/{meme_id}')
    assert delete_response.status_code == 200
    assert delete_response.json()['detail'] == 'Мем удален'
