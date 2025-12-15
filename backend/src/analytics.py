"""
Analytics and metrics tracking for query optimization and business intelligence.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import json
import hashlib

logger = logging.getLogger(__name__)


class Analytics:
    """
    Track interactions, user behavior, and system performance.
    
    Features:
    - Query tracking and categorization
    - Performance metrics
    - Cost tracking
    - User behavior analysis
    - Popular questions identification
    """
    
    def __init__(self):
        """Initialize analytics system."""
        self.interactions = []
        self.query_cache = {}  # Cache for popular queries
        self.user_sessions = {}
        self.metrics = {
            'total_queries': 0,
            'successful_queries': 0,
            'failed_queries': 0,
            'total_cost': 0.0,
            'total_response_time': 0.0,
            'cache_hits': 0,
            'cache_misses': 0
        }
        
        self.query_categories = defaultdict(int)
        self.language_usage = defaultdict(int)
        
    def log_interaction(
        self,
        user_id: str,
        query: str,
        response: str,
        response_time: float,
        tokens_used: int,
        estimated_cost: float,
        language: str,
        provider: str,
        status: str = 'success',
        metadata: Optional[Dict] = None
    ) -> None:
        """
        Log a complete interaction with all metrics.
        
        Args:
            user_id: User identifier (hashed for privacy)
            query: User's query
            response: Bot's response
            response_time: Response time in seconds
            tokens_used: Estimated tokens used
            estimated_cost: Estimated cost in USD
            language: Language used
            provider: LLM provider used
            status: Query status (success/error)
            metadata: Additional metadata
        """
        # Hash sensitive data
        query_hash = hashlib.sha256(query.encode()).hexdigest()[:16]
        
        # Categorize query
        category = self.classify_query(query)
        
        interaction = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'query_hash': query_hash,
            'query_length': len(query),
            'query_category': category,
            'response_length': len(response),
            'response_time_ms': response_time * 1000,
            'tokens_used': tokens_used,
            'estimated_cost': estimated_cost,
            'language': language,
            'provider': provider,
            'status': status,
            'metadata': metadata or {}
        }
        
        self.interactions.append(interaction)
        
        # Update metrics
        self.metrics['total_queries'] += 1
        if status == 'success':
            self.metrics['successful_queries'] += 1
        else:
            self.metrics['failed_queries'] += 1
        
        self.metrics['total_cost'] += estimated_cost
        self.metrics['total_response_time'] += response_time
        
        self.query_categories[category] += 1
        self.language_usage[language] += 1
        
        # Update cache for popular queries
        self._update_query_cache(query_hash, response)
        
        # Update user session
        self._update_user_session(user_id)
        
        logger.debug(f"Logged interaction: {category} query from user {user_id[:8]}")
    
    def classify_query(self, query: str) -> str:
        """
        Classify query into categories.
        
        Args:
            query: User's query
            
        Returns:
            Query category
        """
        query_lower = query.lower()
        
        # Define category keywords
        categories = {
            'staking': ['stake', 'staking', 'validator', 'delegate', 'unstake'],
            'bridging': ['bridge', 'cross-chain', 'transfer', 'multichain'],
            'wallet': ['wallet', 'metamask', 'ledger', 'seed phrase', 'private key'],
            'defi': ['defi', 'liquidity', 'pool', 'yield', 'farm', 'lend', 'borrow'],
            'nft': ['nft', 'token', 'mint', 'opensea', 'collection'],
            'trading': ['trade', 'swap', 'exchange', 'buy', 'sell', 'dex'],
            'security': ['security', 'safe', 'risk', 'scam', 'audit', 'hack'],
            'gas': ['gas', 'fee', 'transaction cost', 'gwei'],
            'general': []  # Default category
        }
        
        for category, keywords in categories.items():
            if any(keyword in query_lower for keyword in keywords):
                return category
        
        return 'general'
    
    def _update_query_cache(self, query_hash: str, response: str) -> None:
        """Update cache for popular queries."""
        if query_hash not in self.query_cache:
            self.query_cache[query_hash] = {
                'response': response,
                'hit_count': 0,
                'last_accessed': datetime.utcnow()
            }
        
        self.query_cache[query_hash]['hit_count'] += 1
        self.query_cache[query_hash]['last_accessed'] = datetime.utcnow()
    
    def _update_user_session(self, user_id: str) -> None:
        """Update user session data."""
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {
                'first_seen': datetime.utcnow(),
                'last_seen': datetime.utcnow(),
                'query_count': 0,
                'languages_used': set(),
                'categories_asked': set()
            }
        
        session = self.user_sessions[user_id]
        session['last_seen'] = datetime.utcnow()
        session['query_count'] += 1
    
    def get_top_questions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get most frequently asked questions.
        
        Args:
            limit: Number of top questions to return
            
        Returns:
            List of top questions with metadata
        """
        sorted_queries = sorted(
            self.query_cache.items(),
            key=lambda x: x[1]['hit_count'],
            reverse=True
        )[:limit]
        
        return [
            {
                'query_hash': query_hash,
                'hit_count': data['hit_count'],
                'response': data['response'],
                'last_accessed': data['last_accessed'].isoformat()
            }
            for query_hash, data in sorted_queries
        ]
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive metrics summary.
        
        Returns:
            Metrics dictionary
        """
        total_queries = self.metrics['total_queries']
        
        summary = {
            'total_queries': total_queries,
            'successful_queries': self.metrics['successful_queries'],
            'failed_queries': self.metrics['failed_queries'],
            'success_rate': (
                self.metrics['successful_queries'] / total_queries * 100
                if total_queries > 0 else 0
            ),
            'total_cost': round(self.metrics['total_cost'], 4),
            'average_cost_per_query': (
                round(self.metrics['total_cost'] / total_queries, 6)
                if total_queries > 0 else 0
            ),
            'average_response_time_ms': (
                round(self.metrics['total_response_time'] / total_queries * 1000, 2)
                if total_queries > 0 else 0
            ),
            'cache_hit_rate': (
                self.metrics['cache_hits'] / 
                (self.metrics['cache_hits'] + self.metrics['cache_misses']) * 100
                if (self.metrics['cache_hits'] + self.metrics['cache_misses']) > 0 
                else 0
            ),
            'top_categories': dict(
                Counter(self.query_categories).most_common(5)
            ),
            'language_distribution': dict(self.language_usage),
            'active_users': len(self.user_sessions),
            'cached_responses': len(self.query_cache)
        }
        
        return summary
    
    def get_user_insights(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get insights for a specific user.
        
        Args:
            user_id: User identifier
            
        Returns:
            User insights or None if user not found
        """
        if user_id not in self.user_sessions:
            return None
        
        session = self.user_sessions[user_id]
        
        # Calculate engagement metrics
        session_duration = (
            session['last_seen'] - session['first_seen']
        ).total_seconds() / 3600  # Hours
        
        return {
            'user_id': user_id[:8],  # Truncated for privacy
            'first_seen': session['first_seen'].isoformat(),
            'last_seen': session['last_seen'].isoformat(),
            'total_queries': session['query_count'],
            'session_duration_hours': round(session_duration, 2),
            'queries_per_hour': (
                round(session['query_count'] / session_duration, 2)
                if session_duration > 0 else 0
            )
        }
    
    def export_to_json(self, filepath: str) -> None:
        """
        Export analytics data to JSON file.
        
        Args:
            filepath: Path to save JSON file
        """
        data = {
            'exported_at': datetime.utcnow().isoformat(),
            'metrics': self.get_metrics_summary(),
            'interactions': self.interactions,
            'top_questions': self.get_top_questions(20)
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        logger.info(f"Analytics exported to {filepath}")
    
    def should_cache_response(self, query_hash: str) -> bool:
        """
        Determine if a response should be cached.
        
        Args:
            query_hash: Hash of the query
            
        Returns:
            True if response is frequently accessed
        """
        if query_hash in self.query_cache:
            return self.query_cache[query_hash]['hit_count'] >= 3
        return False


# Global analytics instance
_analytics: Optional[Analytics] = None


def get_analytics() -> Analytics:
    """Get or create global analytics instance."""
    global _analytics
    if _analytics is None:
        _analytics = Analytics()
    return _analytics
