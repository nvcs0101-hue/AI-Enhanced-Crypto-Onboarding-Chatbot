"""
Usage-based pricing and monetization system.

Tracks usage, enforces limits, and calculates billing.
"""

import logging
from typing import Dict, Optional
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class PricingTier(Enum):
    """Available pricing tiers."""
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class UsageTracker:
    """
    Track user usage and enforce tier limits.
    
    Features:
    - Query counting per user
    - Tier limit enforcement
    - Overage calculation
    - Usage analytics
    """
    
    TIER_CONFIGS = {
        PricingTier.FREE: {
            'queries_per_month': 100,
            'languages': 1,
            'platforms': ['web'],
            'response_time': 'standard',
            'analytics': False,
            'conversation_memory': False,
            'price_monthly': 0,
            'overage_per_query': 0.0  # No overages in free tier
        },
        PricingTier.PRO: {
            'queries_per_month': 10000,
            'languages': 'all',
            'platforms': ['web', 'telegram', 'discord'],
            'response_time': 'fast',
            'analytics': 'basic',
            'conversation_memory': True,
            'custom_branding': True,
            'price_monthly': 299,
            'overage_per_query': 0.05
        },
        PricingTier.ENTERPRISE: {
            'queries_per_month': 'unlimited',
            'languages': 'all',
            'platforms': 'all',
            'response_time': 'realtime',
            'analytics': 'advanced',
            'conversation_memory': True,
            'custom_branding': True,
            'dedicated_instance': True,
            'sla': '99.9%',
            'white_label': True,
            'custom_training': True,
            'priority_support': True,
            'price_monthly': 1999,
            'overage_per_query': 0.0  # Unlimited
        }
    }
    
    def __init__(self):
        """Initialize usage tracker."""
        self.user_usage = {}  # user_id -> usage data
        
    def track_query(self, user_id: str, cost: float = 0.0) -> bool:
        """
        Track a query for a user and check if allowed.
        
        Args:
            user_id: User identifier
            cost: Estimated cost of the query
            
        Returns:
            True if query is allowed, False if limit exceeded
        """
        if user_id not in self.user_usage:
            self.user_usage[user_id] = {
                'tier': PricingTier.FREE,
                'queries_this_month': 0,
                'total_cost': 0.0,
                'month_start': datetime.utcnow(),
                'last_query': None
            }
        
        usage = self.user_usage[user_id]
        
        # Check if new month started
        if datetime.utcnow() - usage['month_start'] > timedelta(days=30):
            usage['queries_this_month'] = 0
            usage['total_cost'] = 0.0
            usage['month_start'] = datetime.utcnow()
        
        # Check tier limit
        tier_config = self.TIER_CONFIGS[usage['tier']]
        query_limit = tier_config['queries_per_month']
        
        if query_limit != 'unlimited' and usage['queries_this_month'] >= query_limit:
            # Check if Pro tier allows overages
            if usage['tier'] == PricingTier.PRO:
                logger.info(f"User {user_id[:8]} exceeded limit, charging overage")
                usage['queries_this_month'] += 1
                usage['total_cost'] += tier_config['overage_per_query']
                usage['last_query'] = datetime.utcnow()
                return True
            else:
                logger.warning(f"User {user_id[:8]} exceeded free tier limit")
                return False
        
        # Track query
        usage['queries_this_month'] += 1
        usage['total_cost'] += cost
        usage['last_query'] = datetime.utcnow()
        
        return True
    
    def upgrade_tier(self, user_id: str, new_tier: PricingTier) -> bool:
        """
        Upgrade a user's tier.
        
        Args:
            user_id: User identifier
            new_tier: New pricing tier
            
        Returns:
            True if upgrade successful
        """
        if user_id not in self.user_usage:
            self.user_usage[user_id] = {
                'tier': new_tier,
                'queries_this_month': 0,
                'total_cost': 0.0,
                'month_start': datetime.utcnow(),
                'last_query': None,
                'upgraded_at': datetime.utcnow()
            }
        else:
            self.user_usage[user_id]['tier'] = new_tier
            self.user_usage[user_id]['upgraded_at'] = datetime.utcnow()
        
        logger.info(f"Upgraded user {user_id[:8]} to {new_tier.value} tier")
        return True
    
    def get_usage(self, user_id: str) -> Dict:
        """
        Get usage statistics for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Usage statistics
        """
        if user_id not in self.user_usage:
            return {
                'tier': PricingTier.FREE.value,
                'queries_this_month': 0,
                'queries_remaining': self.TIER_CONFIGS[PricingTier.FREE]['queries_per_month']
            }
        
        usage = self.user_usage[user_id]
        tier_config = self.TIER_CONFIGS[usage['tier']]
        
        queries_remaining = 'unlimited'
        if tier_config['queries_per_month'] != 'unlimited':
            queries_remaining = max(
                0,
                tier_config['queries_per_month'] - usage['queries_this_month']
            )
        
        return {
            'tier': usage['tier'].value,
            'queries_this_month': usage['queries_this_month'],
            'queries_remaining': queries_remaining,
            'total_cost': round(usage['total_cost'], 2),
            'month_start': usage['month_start'].isoformat(),
            'last_query': usage['last_query'].isoformat() if usage['last_query'] else None
        }
    
    def calculate_bill(self, user_id: str) -> Dict:
        """
        Calculate monthly bill for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Billing information
        """
        if user_id not in self.user_usage:
            return {
                'tier': PricingTier.FREE.value,
                'base_price': 0,
                'overage_charge': 0,
                'total': 0
            }
        
        usage = self.user_usage[user_id]
        tier_config = self.TIER_CONFIGS[usage['tier']]
        
        base_price = tier_config['price_monthly']
        overage_charge = 0
        
        # Calculate overages for Pro tier
        if usage['tier'] == PricingTier.PRO:
            query_limit = tier_config['queries_per_month']
            if usage['queries_this_month'] > query_limit:
                overages = usage['queries_this_month'] - query_limit
                overage_charge = overages * tier_config['overage_per_query']
        
        return {
            'tier': usage['tier'].value,
            'base_price': base_price,
            'queries_used': usage['queries_this_month'],
            'overage_queries': max(0, usage['queries_this_month'] - tier_config.get('queries_per_month', 0)),
            'overage_charge': round(overage_charge, 2),
            'total': round(base_price + overage_charge, 2),
            'period': f"{usage['month_start'].strftime('%Y-%m-%d')} to {(usage['month_start'] + timedelta(days=30)).strftime('%Y-%m-%d')}"
        }


# Global usage tracker
_usage_tracker: Optional[UsageTracker] = None


def get_usage_tracker() -> UsageTracker:
    """Get or create global usage tracker instance."""
    global _usage_tracker
    if _usage_tracker is None:
        _usage_tracker = UsageTracker()
    return _usage_tracker
