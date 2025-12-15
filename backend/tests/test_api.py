"""
Test suite for Flask API endpoints.
"""

import pytest
import json
from unittest.mock import patch, Mock
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app as flask_app


@pytest.fixture
def client():
    """Create test client."""
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client


class TestHealthEndpoint:
    """Test cases for /api/health endpoint."""
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get('/api/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data


class TestLanguagesEndpoint:
    """Test cases for /api/languages endpoint."""
    
    def test_get_languages(self, client):
        """Test get languages endpoint."""
        response = client.get('/api/languages')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'languages' in data
        assert len(data['languages']) > 0


class TestChatEndpoint:
    """Test cases for /api/chat endpoint."""
    
    @patch('app.query_rag')
    def test_chat_success(self, mock_query, client):
        """Test successful chat request."""
        mock_query.return_value = {
            'answer': 'Test response',
            'status': 'success'
        }
        
        response = client.post(
            '/api/chat',
            data=json.dumps({'message': 'Test question'}),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'response' in data
    
    def test_chat_missing_message(self, client):
        """Test chat endpoint with missing message."""
        response = client.post(
            '/api/chat',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_chat_empty_message(self, client):
        """Test chat endpoint with empty message."""
        response = client.post(
            '/api/chat',
            data=json.dumps({'message': ''}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
    
    def test_chat_wrong_content_type(self, client):
        """Test chat endpoint with wrong content type."""
        response = client.post(
            '/api/chat',
            data='message=test',
            content_type='application/x-www-form-urlencoded'
        )
        
        assert response.status_code == 400
    
    @patch('app.query_rag')
    def test_chat_with_language(self, mock_query, client):
        """Test chat with language parameter."""
        mock_query.return_value = {
            'answer': 'Test response',
            'status': 'success'
        }
        
        response = client.post(
            '/api/chat',
            data=json.dumps({
                'message': 'Test question',
                'language': 'es'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'language' in data


class TestRateLimiting:
    """Test cases for rate limiting."""
    
    @patch('app.query_rag')
    def test_rate_limit_not_exceeded(self, mock_query, client):
        """Test that rate limit allows normal usage."""
        mock_query.return_value = {
            'answer': 'Test',
            'status': 'success'
        }
        
        # Make several requests within limit
        for _ in range(5):
            response = client.post(
                '/api/chat',
                data=json.dumps({'message': 'Test'}),
                content_type='application/json'
            )
            assert response.status_code == 200


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
