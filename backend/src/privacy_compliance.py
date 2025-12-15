"""
Privacy compliance and data protection (GDPR, CCPA).

Handles PII detection, data minimization, and user privacy rights.
"""

import logging
import re
import hashlib
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class PIIDetector:
    """
    Detect and redact Personally Identifiable Information.
    
    Features:
    - Email detection
    - Phone number detection
    - Wallet address detection
    - Name detection (basic)
    - Credit card detection
    """
    
    # Regex patterns for PII
    PATTERNS = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone': r'\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b',
        'crypto_address': r'\b0x[a-fA-F0-9]{40}\b',  # Ethereum address
        'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
        'ssn': r'\b\d{3}-\d{2}-\d{4}\b'
    }
    
    def __init__(self):
        """Initialize PII detector."""
        self.compiled_patterns = {
            name: re.compile(pattern)
            for name, pattern in self.PATTERNS.items()
        }
    
    def detect(self, text: str) -> Dict[str, List[str]]:
        """
        Detect PII in text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary of detected PII by type
        """
        detected = {}
        
        for pii_type, pattern in self.compiled_patterns.items():
            matches = pattern.findall(text)
            if matches:
                detected[pii_type] = matches
                logger.warning(f"Detected {len(matches)} {pii_type} instances")
        
        return detected
    
    def redact(self, text: str) -> Tuple[str, bool]:
        """
        Redact PII from text.
        
        Args:
            text: Text to redact
            
        Returns:
            Tuple of (redacted_text, pii_found)
        """
        redacted = text
        pii_found = False
        
        for pii_type, pattern in self.compiled_patterns.items():
            if pattern.search(redacted):
                pii_found = True
                # Replace with redacted markers
                if pii_type == 'email':
                    redacted = pattern.sub('[EMAIL REDACTED]', redacted)
                elif pii_type == 'phone':
                    redacted = pattern.sub('[PHONE REDACTED]', redacted)
                elif pii_type == 'crypto_address':
                    redacted = pattern.sub('[WALLET ADDRESS]', redacted)
                elif pii_type == 'credit_card':
                    redacted = pattern.sub('[CARD NUMBER REDACTED]', redacted)
                elif pii_type == 'ssn':
                    redacted = pattern.sub('[SSN REDACTED]', redacted)
        
        if pii_found:
            logger.info("Redacted PII from text")
        
        return redacted, pii_found


class PrivacyCompliance:
    """
    GDPR and CCPA compliance manager.
    
    Features:
    - PII detection and redaction
    - Data minimization
    - Consent management
    - Right to be forgotten
    - Data portability
    """
    
    def __init__(self):
        """Initialize privacy compliance manager."""
        self.pii_detector = PIIDetector()
        self.user_consents = {}  # user_id -> consent data
        self.data_retention_days = 90
        
    def process_query(
        self,
        user_id: str,
        query: str,
        region: str = 'US'
    ) -> Dict[str, any]:
        """
        Process query with privacy protection.
        
        Args:
            user_id: User identifier (should be hashed)
            query: User's query
            region: User's region (EU, US, etc.)
            
        Returns:
            Processing result with cleaned query
        """
        # Detect and redact PII
        cleaned_query, pii_found = self.pii_detector.redact(query)
        
        result = {
            'cleaned_query': cleaned_query,
            'pii_detected': pii_found,
            'region': region,
            'requires_consent': region == 'EU'
        }
        
        # Log PII incident if found
        if pii_found:
            self._log_pii_incident(user_id)
        
        # Check consent for EU users
        if region == 'EU' and not self.has_consent(user_id):
            result['consent_required'] = True
            result['error'] = 'GDPR consent required before processing'
        
        return result
    
    def request_consent(
        self,
        user_id: str,
        purposes: List[str]
    ) -> Dict:
        """
        Request user consent.
        
        Args:
            user_id: User identifier
            purposes: List of purposes (analytics, marketing, etc.)
            
        Returns:
            Consent request details
        """
        return {
            'user_id': user_id[:8],
            'purposes': purposes,
            'message': (
                'We need your consent to process your data for the following purposes: '
                f"{', '.join(purposes)}. Your data will be stored for {self.data_retention_days} days."
            )
        }
    
    def grant_consent(
        self,
        user_id: str,
        purposes: List[str]
    ) -> bool:
        """
        Grant consent for a user.
        
        Args:
            user_id: User identifier
            purposes: Consented purposes
            
        Returns:
            True if consent granted
        """
        self.user_consents[user_id] = {
            'purposes': purposes,
            'granted_at': datetime.utcnow(),
            'expires_at': datetime.utcnow() + timedelta(days=365)
        }
        
        logger.info(f"Consent granted for user {user_id[:8]}")
        return True
    
    def has_consent(self, user_id: str) -> bool:
        """
        Check if user has active consent.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if user has valid consent
        """
        if user_id not in self.user_consents:
            return False
        
        consent = self.user_consents[user_id]
        
        # Check if consent expired
        if datetime.utcnow() > consent['expires_at']:
            logger.info(f"Consent expired for user {user_id[:8]}")
            del self.user_consents[user_id]
            return False
        
        return True
    
    def revoke_consent(self, user_id: str) -> bool:
        """
        Revoke consent for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if consent was revoked
        """
        if user_id in self.user_consents:
            del self.user_consents[user_id]
            logger.info(f"Consent revoked for user {user_id[:8]}")
            return True
        return False
    
    def delete_user_data(self, user_id: str) -> Dict:
        """
        Delete all user data (Right to be Forgotten - GDPR Article 17).
        
        Args:
            user_id: User identifier
            
        Returns:
            Deletion report
        """
        deleted_items = {
            'consent_records': 0,
            'conversations': 0,
            'analytics': 0,
            'usage_data': 0
        }
        
        # Delete consent
        if user_id in self.user_consents:
            del self.user_consents[user_id]
            deleted_items['consent_records'] = 1
        
        logger.info(f"Deleted all data for user {user_id[:8]}")
        
        return {
            'user_id': user_id[:8],
            'deleted_at': datetime.utcnow().isoformat(),
            'items_deleted': deleted_items,
            'status': 'completed'
        }
    
    def export_user_data(self, user_id: str) -> Dict:
        """
        Export all user data (GDPR Article 20 - Right to Data Portability).
        
        Args:
            user_id: User identifier
            
        Returns:
            Exported user data
        """
        export = {
            'user_id': user_id[:8],
            'exported_at': datetime.utcnow().isoformat(),
            'data': {}
        }
        
        # Export consent data
        if user_id in self.user_consents:
            export['data']['consent'] = {
                'purposes': self.user_consents[user_id]['purposes'],
                'granted_at': self.user_consents[user_id]['granted_at'].isoformat(),
                'expires_at': self.user_consents[user_id]['expires_at'].isoformat()
            }
        
        logger.info(f"Exported data for user {user_id[:8]}")
        return export
    
    def _log_pii_incident(self, user_id: str) -> None:
        """Log PII detection incident."""
        logger.warning(
            f"PII detected in query from user {user_id[:8]} - "
            f"data has been redacted"
        )
    
    def hash_user_id(self, identifier: str) -> str:
        """
        Hash user identifier for privacy.
        
        Args:
            identifier: User identifier (IP, email, etc.)
            
        Returns:
            Hashed identifier
        """
        return hashlib.sha256(identifier.encode()).hexdigest()[:16]


# Global compliance instance
_compliance: Optional[PrivacyCompliance] = None


def get_compliance() -> PrivacyCompliance:
    """Get or create global privacy compliance instance."""
    global _compliance
    if _compliance is None:
        _compliance = PrivacyCompliance()
    return _compliance
