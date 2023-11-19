import pytest
from flask import template_rendered
from contextlib import contextmanager
from app import app

# This fixture will be used by each test to create a test client
@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

# Context manager to capture templates rendered during testing
@contextmanager
def captured_templates(app):
    recorded = []
    def record(sender, template, context, **extra):
        recorded.append((template, context))
    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)

# Test for the health endpoint
def test_health_endpoint(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.data.decode('utf-8') == 'healthy'

# Test for the home endpoint
def test_home_endpoint(client):
    with captured_templates(app) as templates:
        response = client.get('/')
        assert response.status_code == 200
        assert len(templates) == 1
        template, context = templates[0]
        assert template.name == 'index.html'

# Test for the get_quote endpoint
def test_quote_endpoint(client, monkeypatch):
    class MockResponse:
        @staticmethod
        def text():
            return "Mock quote"

    # Patching the requests.get method to return a mock response
    monkeypatch.setattr(requests, 'get', lambda url: MockResponse())

    with captured_templates(app) as templates:
        response = client.get('/get_quote')
        assert response.status_code == 200
        assert len(templates) == 1
        template, context = templates[0]
        assert template.name == 'quote.html'
        assert 'quote' in context
        assert context['quote'] == 'Mock quote'
