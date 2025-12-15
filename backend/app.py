"""
Flask API server for the AI-Enhanced Crypto Onboarding Chatbot.

This module provides REST API endpoints for chat interactions, health checks,
and rate limiting for the crypto onboarding assistant.
"""

import os
import logging
from typing import Dict, Any
from datetime import datetime

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
import hashlib

from src.rag_pipeline import query_rag
from src.analytics import get_analytics
from src.llm_manager import get_llm_manager
from src.conversation_memory import get_conversation_memory
from src.usage_tracker import get_usage_tracker, PricingTier
from src.privacy_compliance import get_compliance

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configure CORS
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Configure rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per hour"],
    storage_uri="memory://"
)

# Supported languages
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'es': 'Español',
    'zh': '中文',
    'hi': 'हिन्दी',
    'fr': 'Français',
    'de': 'Deutsch',
    'ja': '日本語',
    'ko': '한국어',
    'pt': 'Português',
    'ru': 'Русский'
}


@app.route('/')
def index():
    """Serve the main page."""
    return jsonify({
        "name": "AI-Enhanced Crypto Onboarding Chatbot",
        "version": "1.0.0",
        "description": "RAG-powered chatbot for crypto protocol onboarding",
        "endpoints": {
            "/api/chat": "POST - Send chat messages",
            "/api/health": "GET - Health check",
            "/api/languages": "GET - Get supported languages",
            "/docs": "GET - API documentation"
        }
    })


@app.route('/api/health', methods=['GET'])
def health():
    """
    Health check endpoint.
    
    Returns:
        JSON response with health status
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'crypto-onboarding-chatbot'
    }), 200


@app.route('/api/languages', methods=['GET'])
def get_languages():
    """
    Get list of supported languages.
    
    Returns:
        JSON response with supported languages
    """
    return jsonify({
        'languages': [
            {'code': code, 'name': name}
            for code, name in SUPPORTED_LANGUAGES.items()
        ]
    }), 200


@app.route('/api/chat', methods=['POST']) with advanced features.
    
    Request JSON:
        {
            "message": "User's question",
            "language": "en" (optional, default: "en"),
            "return_sources": false (optional, default: false),
            "user_id": "optional_user_identifier"
        }
    
    Returns:
        JSON response with AI answer and metadata
    """
    try:
        # Validate request
        if not request.is_json:
            return jsonify({
                'error': 'Content-Type must be application/json'
            }), 400
        
        data = request.get_json()
        
        # Extract and validate parameters
        user_message = data.get('message', '').strip()
        if not user_message:
            return jsonify({
                'error': 'No message provided',
                'details': 'The "message" field is required and cannot be empty'
            }), 400
        
        # Validate message length
        if len(user_message) > 1000:
            return jsonify({
                'error': 'Message too long',
                'details': 'Message must be less than 1000 characters'
            }), 400
        
        # Get language
        language_code = data.get('language', 'en').lower()
        language_name = SUPPORTED_LANGUAGES.get(language_code, 'English')
        
        # Get return_sources flag
        return_sources = data.get('return_sources', False)
        
        # Get or generate user_id (hash IP for privacy)
        user_id = data.get('user_id') or hashlib.sha256(
            request.remote_addr.encode()
        ).hexdigest()[:16]
        
        # Check usage limits
        usage_tracker = get_usage_tracker()
        if not usage_tracker.track_query(user_id):
            return jsonify({
                'error': 'Query limit exceeded',
                'details': 'You have reached your monthly query limit. Please upgrade your plan.',
                'usage': usage_tracker.get_usage(user_id)
            }), 429
        
        # Privacy compliance check
        compliance = get_compliance()
        region = request.headers.get('CF-IPCountry', 'US')  # Cloudflare country header
        privacy_result = compliance.process_query(user_id, user_message, region)
        
        if privacy_result.get('consent_required'):
            return jsonify({
                'error': 'Consent required',
                'details': privacy_result.get('error'),
                'consent_url': '/api/consent'
            }), 403
        
        # Use cleaned query if PII was detected
        final_query = privacy_result.get('cleaned_query', user_message)
        
        logger.info(f"Processing chat request - Language: {language_name}, User: {user_id[:8]}")
        
        # Get RAG response with all features
        response = query_rag(
            user_question=final_query,
            language=language_name,
            return_sources=return_sources,
            user_id=user_id
        )
        
        # Build response
        result = {
            'response': response.get('answer', ''),
            'status': response.get('status', 'success'),
            'language': language_name,
            'timestamp': datetime.utcnow().isoformat(),
            'provider': response.get('provider'),
            'response_time': response.get('response_time')
        }
        
        # Add validation info
        if 'validation' in response:
            result['validation'] = response['validation']
        
        # Add sources if requested
        if return_sources and 'sources' in response:
            result['sources'] = response['sources']
        
        # Add error details if present
        if 'error' in response:
            result['error_details'] = response['error']
        
        loggeapi/stats', methods=['GET'])
def get_stats():
    """
    Get system statistics and analytics.
    
    Returns:
        JSON response with comprehensive stats
    """
    try:
        analytics = get_analytics()
        llm_manager = get_llm_manager()
        conversation_memory = get_conversation_memory()
        
        stats = {
            'analytics': analytics.get_metrics_summary(),
            'llm_usage': llm_manager.get_stats(),
            'conversations': conversation_memory.get_all_stats(),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return jsonify(stats), 200
    
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/top-questions', methods=['GET'])
def get_top_questions():
    """
    Get most frequently asked questions.
    
    Query params:
        limit: Number of questions to return (default: 20)
    
    Returns:
        JSON response with top questions
    """
    try:
        limit = int(request.args.get('limit', 20))
        analytics = get_analytics()
        
        top_questions = analytics.get_top_questions(limit)
        
        return jsonify({
            'top_questions': top_questions,
            'count': len(top_questions)
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting top questions: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/conversation/<user_id>', methods=['GET'])
def get_conversation(user_id):
    """
    Get conversation history for a user.
    
    Args:
        user_id: User identifier
    
    Returns:
        JSON response with conversation history
    """
    try:
        conversation_memory = get_conversation_memory()
        
        messages = conversation_memory.get_messages(user_id)
        stats = conversation_memory.get_conversation_stats(user_id)
        
        return jsonify({
            'messages': [
                {
                    'role': msg['role'],
                    'content': msg['content'],
                    'timestamp': msg['timestamp'].isoformat()
                }
                for msg in messages
            ],
            'stats': stats
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting conversation: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/conversation/<user_id>', methods=['DELETE'])
def clear_conversation(user_id):
    """
    Clear conversation history for a user.
    
    Args:
        user_id: User identifier
    
    Returns:
        JSON response with confirmation
    """
    try:
        conversation_memory = get_conversation_memory()
        cleared = conversation_memory.clear_conversation(user_id)
        
        if cleared:
            return jsonify({
                'status': 'success',
                'message': f'Conversation cleared for user {user_id[:8]}'
            }), 200
        else:
            return jsonify({
                'status': 'not_found',
                'message': 'No conversation found for this user'
            }), 404
    
    except Exception as e:
        logger.error(f"Error clearing conversation: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/usage/<user_id>', methods=['GET'])
def get_usage(user_id):
    """
    Get usage statistics for a user.
    
    Args:
        user_id: User identifier
    
    Returns:
        JSON response with usage data
    """
    try:
        usage_tracker = get_usage_tracker()
        usage = usage_tracker.get_usage(user_id)
        
        return jsonify(usage), 200
    
    except Exception as e:
        logger.error(f"Error getting usage: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/billing/<user_id>', methods=['GET'])
def get_billing(user_id):
    """
    Get billing information for a user.
    
    Args:
        user_id: User identifier
    
    Returns:
        JSON response with billing details
    """
    try:
        usage_tracker = get_usage_tracker()
        bill = usage_tracker.calculate_bill(user_id)
        
        return jsonify(bill), 200
    
    except Exception as e:
        logger.error(f"Error calculating billing: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/upgrade', methods=['POST'])
def upgrade_tier():
    """
    Upgrade user's pricing tier.
    
    Request JSON:
        {
            "user_id": "user_identifier",
            "tier": "pro" or "enterprise"
        }
    
    Returns:
        JSON response with upgrade confirmation
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        tier_name = data.get('tier', '').lower()
        
        if not user_id or not tier_name:
            return jsonify({
                'error': 'Missing required fields',
                'details': 'user_id and tier are required'
            }), 400
        
        # Validate tier
        try:
            tier = PricingTier(tier_name)
        except ValueError:
            return jsonify({
                'error': 'Invalid tier',
                'details': f'Valid tiers: {[t.value for t in PricingTier]}'
            }), 400
        
        usage_tracker = get_usage_tracker()
        success = usage_tracker.upgrade_tier(user_id, tier)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': f'Upgraded to {tier.value} tier',
                'usage': usage_tracker.get_usage(user_id)
            }), 200
        else:
            return jsonify({
                'error': 'Upgrade failed'
            }), 500
    
    except Exception as e:
        logger.error(f"Error upgrading tier: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/consent', methods=['POST'])
def grant_consent():
    """
    Grant GDPR consent for a user.
    
    Request JSON:
        {
            "user_id": "user_identifier",
            "purposes": ["analytics", "personalization"]
        }
    
    Returns:
        JSON response with consent confirmation
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        purposes = data.get('purposes', [])
        
        if not user_id or not purposes:
            return jsonify({
                'error': 'Missing required fields',
                'details': 'user_id and purposes are required'
            }), 400
        
        compliance = get_compliance()
        success = compliance.grant_consent(user_id, purposes)
        
        return jsonify({
            'status': 'success',
            'message': 'Consent granted',
            'user_id': user_id[:8],
            'purposes': purposes
        }), 200
    
    except Exception as e:
        logger.error(f"Error granting consent: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/data/<user_id>', methods=['DELETE'])
def delete_user_data(user_id):
    """
    Delete all user data (GDPR Right to be Forgotten).
    
    Args:
        user_id: User identifier
    
    Returns:
        JSON response with deletion confirmation
    """
    try:
        compliance = get_compliance()
        conversation_memory = get_conversation_memory()
        
        # Delete from all systems
        deletion_report = compliance.delete_user_data(user_id)
        conversation_memory.clear_conversation(user_id)
        
        return jsonify({
            'status': 'success',
            'message': 'All user data deleted',
            'report': deletion_report
        }), 200
    
    except Exception as e:
        logger.error(f"Error deleting user data: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/data/<user_id>/export', methods=['GET'])
def export_user_data(user_id):
    """
    Export all user data (GDPR Right to Data Portability).
    
    Args:
        user_id: User identifier
    
    Returns:
        JSON response with exported data
    """
    try:
        compliance = get_compliance()
        analytics = get_analytics()
        conversation_memory = get_conversation_memory()
        usage_tracker = get_usage_tracker()
        
        # Collect all user data
        export = compliance.export_user_data(user_id)
        export['data']['usage'] = usage_tracker.get_usage(user_id)
        export['data']['conversation_stats'] = conversation_memory.get_conversation_stats(user_id)
        export['data']['analytics'] = analytics.get_user_insights(user_id)
        
        return jsonify(export), 200
    
    except Exception as e:
        logger.error(f"Error exporting user data: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/r.info(f"Chat request processed successfully via {response.get('provider')}
        if 'error' in response:
            result['error_details'] = response['error']
        
        logger.info("Chat request processed successfully")
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'details': 'An unexpected error occurred while processing your request',
            'status': 'error',
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@app.route('/docs')
def docs():
    """Serve API documentation."""
    documentation = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>API Documentation - Crypto Onboarding Chatbot</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 900px;
                margin: 50px auto;
                padding: 20px;
                line-height: 1.6;
            }
            h1, h2, h3 { color: #333; }
            code {
                background: #f4f4f4;
                padding: 2px 6px;
                border-radius: 3px;
            }
            pre {
                background: #f4f4f4;
                padding: 15px;
                border-radius: 5px;
                overflow-x: auto;
            }
            .endpoint {
                background: #e8f5e9;
                padding: 15px;
                margin: 20px 0;
                border-left: 4px solid #4caf50;
            }
        </style>
    </head>
    <body>
        <h1>🤖 Crypto Onboarding Chatbot API</h1>
        <p>AI-powered onboarding assistant for crypto protocols using RAG technology.</p>
        
        <h2>Endpoints</h2>
        
        <div class="endpoint">
            <h3>POST /api/chat</h3>
            <p>Send a message to the chatbot and receive an AI-generated response.</p>
            <p><strong>Rate Limit:</strong> 20 requests per minute</p>
            <p><strong>Request Body:</strong></p>
            <pre>{
  "message": "How do I stake my tokens?",
  "language": "en",
  "return_sources": false
}</pre>
            <p><strong>Response:</strong></p>
            <pre>{
  "response": "To stake your tokens, follow these steps...",
  "status": "success",
  "language": "English",
  "timestamp": "2025-12-15T10:30:00Z"
}</pre>
        </div>
        
        <div class="endpoint">
            <h3>GET /api/health</h3>
            <p>Check the health status of the API.</p>
            <p><strong>Response:</strong></p>
            <pre>{
  "status": "healthy",
  "timestamp": "2025-12-15T10:30:00Z",
  "service": "crypto-onboarding-chatbot"
}</pre>
        </div>
        
        <div class="endpoint">
            <h3>GET /api/languages</h3>
            <p>Get list of supported languages.</p>
            <p><strong>Response:</strong></p>
            <pre>{
  "languages": [
    {"code": "en", "name": "English"},
    {"code": "es", "name": "Español"},
    ...
  ]
}</pre>
        </div>
        
        <h2>Supported Languages</h2>
        <ul>
            <li>English (en)</li>
            <li>Español (es)</li>
            <li>中文 (zh)</li>
            <li>हिन्दी (hi)</li>
            <li>Français (fr)</li>
            <li>Deutsch (de)</li>
            <li>日本語 (ja)</li>
            <li>한국어 (ko)</li>
            <li>Português (pt)</li>
            <li>Русский (ru)</li>
        </ul>
        
        <h2>Error Responses</h2>
        <p>The API returns appropriate HTTP status codes and error messages:</p>
        <ul>
            <li><code>400</code> - Bad Request (missing or invalid parameters)</li>
            <li><code>429</code> - Too Many Requests (rate limit exceeded)</li>
            <li><code>500</code> - Internal Server Error</li>
        </ul>
    </body>
    </html>
    """
    return documentation


@app.errorhandler(429)
def ratelimit_handler(e):
    """Handle rate limit errors."""
    return jsonify({
        'error': 'Rate limit exceeded',
        'details': 'Too many requests. Please try again later.',
        'status': 'error'
    }), 429


@app.errorhandler(404)
def not_found_handler(e):
    """Handle 404 errors."""
    return jsonify({
        'error': 'Not found',
        'details': 'The requested endpoint does not exist',
        'status': 'error'
    }), 404


@app.errorhandler(500)
def internal_error_handler(e):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {str(e)}", exc_info=True)
    return jsonify({
        'error': 'Internal server error',
        'details': 'An unexpected error occurred',
        'status': 'error'
    }), 500


if __name__ == '__main__':
    # Check for required environment variables
    if not os.getenv('OPENAI_API_KEY'):
        logger.warning(
            "OPENAI_API_KEY not set. The chatbot will not function properly. "
            "Please set it in your .env file or environment."
        )
    
    # Get configuration from environment
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Flask server on {host}:{port}")
    logger.info(f"Debug mode: {debug}")
    
    app.run(host=host, port=port, debug=debug)
