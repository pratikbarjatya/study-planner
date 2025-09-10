import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'AI Study Planner' in response.data

def test_chat_no_message(client):
    response = client.post('/api/chat', json={})
    assert response.status_code == 400
    data = response.get_json()
    assert data['status'] == 'error'
    assert 'No message provided' in data['error']

def test_chat_message_too_long(client):
    long_message = 'a' * 1001
    response = client.post('/api/chat', json={'message': long_message})
    assert response.status_code == 400
    data = response.get_json()
    assert data['status'] == 'error'
    assert 'Message too long' in data['error']

def test_chat_llm_client_unavailable(monkeypatch, client):
    monkeypatch.setattr('app.client', None)
    response = client.post('/api/chat', json={'message': 'Hello'})
    assert response.status_code == 500
    data = response.get_json()
    assert data['status'] == 'error'
    assert 'LLM client not available' in data['error']

def test_chat_success(monkeypatch, client):
    class DummyClient:
        def generate_response(self, msg):
            return "Test response"
    monkeypatch.setattr('app.client', DummyClient())
    response = client.post('/api/chat', json={'message': 'Hello'})
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert data['response'] == 'Test response'