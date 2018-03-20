import requests


def test_integrations():
    response = requests.get('http://server:8000/')
    assert response.status_code == 200
