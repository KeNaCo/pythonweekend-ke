import pytest
from uuid import uuid4

from app import make_app


@pytest.fixture
def client():
    app = make_app()
    client = app.test_client()
    return client


def test_v1_charge(client):
    request_bodies = (
        {},
        {'currency': "CZK"},
        {'amount': "123.5", 'currency': "CZKK"}
    )
    for request_body in request_bodies:
        response = client.post('/v1/charge', json=request_body)
        assert response.status_code == 400


def test_v2_authorize(client):
    request_body = {
        'merchant': 'Company',
        'amount_of_money': {
            'amount': 12345,
            'currency': 'CZK'
        }
    }
    response = client.post('/v2/authorize', json=request_body)
    assert response.status_code == 200
    assert 'payment_reference' in response.json


def test_v2_capture(client):
    request_body = {
        'payment_reference': uuid4()
    }
    response = client.post('/v2/capture', json=request_body)
    assert response.status_code == 200

    request_body = {
        'payment_reference': "reference"
    }
    response = client.post('/v2/capture', json=request_body)
    assert response.status_code == 400
    assert 'reason' in response.json

    request_body = {}
    response = client.post('/v2/capture', json=request_body)
    assert response.status_code == 400
    assert 'reason' in response.json


def test_v3_authorize(client):
    request_body = {
        'amount': "123",
        'currency': "CZK"
    }
    response = client.post('/v3/authorize', json=request_body)
    assert response.status_code == 200
    assert 'status' in response.json
    assert response.json['status'] == 200
    assert 'payment_id' in response.json


def test_v3_capture(client):
    payment_id = uuid4()
    response = client.post(f'/v3/capture/{payment_id}')
    assert response.status_code == 200
    assert 'status' in response.json
    assert response.json['status'] == 200
