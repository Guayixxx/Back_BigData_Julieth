import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_test_endpoint(client):
    response = client.get('/test')
    assert response.status_code == 200
    assert response.json == {"message": "Hola Mundo"}
