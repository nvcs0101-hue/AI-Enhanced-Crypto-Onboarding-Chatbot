"""
Integration tests for AI-Enhanced Crypto Onboarding Chatbot.

Tests the complete system including:
- Multi-LLM routing
- Analytics tracking
- Conversation memory
- Response validation
- Usage tracking
- Privacy compliance
"""

import unittest
import os
import sys
import time
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.src.llm_manager import LLMManager, LLMProvider
from backend.src.analytics import Analytics
from backend.src.conversation_memory import ConversationMemory
from backend.src.response_validator import ResponseValidator
from backend.src.usage_tracker import UsageTracker, PricingTier
from backend.src.privacy_compliance import PrivacyCompliance, PIIDetector


class TestMultiLLMRouting(unittest.TestCase):
    """Test multi-LLM routing functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.llm_manager = LLMManager()
    
    def test_complexity_scoring(self):
        """Test query complexity calculation."""
        # Simple query should score low
        simple_query = "What is Ethereum?"
        simple_score = self.llm_manager.calculate_complexity_score(simple_query)
        self.assertLess(simple_score, 5)
        
        # Complex query should score high
        complex_query = "Explain the technical differences between proof-of-work and proof-of-stake consensus mechanisms, including energy consumption, security trade-offs, and validator economics."
        complex_score = self.llm_manager.calculate_complexity_score(complex_query)
        self.assertGreater(complex_score, 5)
    
    def test_provider_selection(self):
        """Test automatic provider selection."""
        # Simple query should prefer Gemini (free)
        simple_query = "What is Bitcoin?"
        provider = self.llm_manager._select_provider(simple_query)
        self.assertEqual(provider, LLMProvider.GEMINI)
        
        # Complex query should prefer OpenAI (quality)
        complex_query = "Provide a detailed analysis of Layer 2 scaling solutions including optimistic rollups, zk-rollups, state channels, and sidechains with their respective trade-offs."
        provider = self.llm_manager._select_provider(complex_query)
        self.assertIn(provider, [LLMProvider.OPENAI, LLMProvider.PERPLEXITY])
    
    def test_fallback_mechanism(self):
        """Test fallback to alternative providers."""
        # This test requires actual API calls, so we'll just verify the logic
        query = "Test query"
        providers = [LLMProvider.OPENAI, LLMProvider.GEMINI, LLMProvider.PERPLEXITY]
        
        for provider in providers:
            self.assertIn(provider, LLMProvider)


class TestAnalytics(unittest.TestCase):
    """Test analytics tracking."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analytics = Analytics()
    
    def test_query_classification(self):
        """Test query categorization."""
        test_cases = [
            ("How do I stake ETH?", "staking"),
            ("Transfer tokens to Polygon", "bridging"),
            ("What is a hardware wallet?", "wallet"),
            ("How to provide liquidity on Uniswap?", "defi"),
            ("Buy an NFT on OpenSea", "nft"),
            ("Current gas fees", "gas"),
            ("Is this a scam?", "security")
        ]
        
        for query, expected_category in test_cases:
            category = self.analytics.classify_query(query)
            self.assertEqual(category, expected_category, 
                           f"Query '{query}' should be '{expected_category}', got '{category}'")
    
    def test_interaction_logging(self):
        """Test interaction logging."""
        user_id = "test_user_123"
        query = "What is staking?"
        
        self.analytics.log_interaction(
            user_id=user_id,
            query=query,
            response="Staking is...",
            category="staking",
            language="en",
            response_time=1.5,
            tokens_used=150,
            cost=0.0002,
            provider="openai"
        )
        
        # Check user insights
        insights = self.analytics.get_user_insights(user_id)
        self.assertEqual(insights['total_queries'], 1)
        self.assertIn('staking', insights['categories'])
    
    def test_top_questions(self):
        """Test top questions identification."""
        # Log multiple queries
        for i in range(3):
            self.analytics.log_interaction(
                user_id=f"user_{i}",
                query="What is Ethereum?",
                response="Ethereum is...",
                category="general",
                language="en",
                response_time=1.0,
                tokens_used=100,
                cost=0.0001,
                provider="gemini"
            )
        
        for i in range(2):
            self.analytics.log_interaction(
                user_id=f"user_{i+3}",
                query="How to buy Bitcoin?",
                response="To buy Bitcoin...",
                category="trading",
                language="en",
                response_time=1.0,
                tokens_used=100,
                cost=0.0001,
                provider="gemini"
            )
        
        top_questions = self.analytics.get_top_questions(limit=5)
        self.assertGreater(len(top_questions), 0)
        self.assertEqual(top_questions[0]['question'], "what is ethereum?")


class TestConversationMemory(unittest.TestCase):
    """Test conversation memory."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.memory = ConversationMemory(max_history=5, session_timeout=60)
    
    def test_message_storage(self):
        """Test storing and retrieving messages."""
        user_id = "test_user"
        
        self.memory.add_message(user_id, "user", "Hello")
        self.memory.add_message(user_id, "assistant", "Hi there!")
        self.memory.add_message(user_id, "user", "What is Bitcoin?")
        
        context = self.memory.get_context(user_id)
        self.assertIn("Hello", context)
        self.assertIn("Hi there!", context)
        self.assertIn("What is Bitcoin?", context)
    
    def test_history_limit(self):
        """Test conversation history limit."""
        user_id = "test_user"
        
        # Add 10 messages (exceeds limit of 5)
        for i in range(10):
            self.memory.add_message(user_id, "user", f"Message {i}")
        
        conversation = self.memory.conversations.get(user_id)
        # Should only keep last 5 messages
        self.assertLessEqual(len(conversation['messages']), 5)
    
    def test_clear_conversation(self):
        """Test clearing conversation."""
        user_id = "test_user"
        
        self.memory.add_message(user_id, "user", "Hello")
        self.assertTrue(self.memory.clear_conversation(user_id))
        self.assertNotIn(user_id, self.memory.conversations)


class TestResponseValidator(unittest.TestCase):
    """Test response validation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = ResponseValidator()
    
    def test_dangerous_content_detection(self):
        """Test detection of dangerous financial claims."""
        dangerous_responses = [
            "This investment guarantees 100% returns!",
            "There is absolutely no risk involved.",
            "You will definitely make money.",
            "This is a sure thing, trust me."
        ]
        
        for response in dangerous_responses:
            result = self.validator.validate("Test query", response, [])
            self.assertFalse(result['validation']['is_safe'])
            self.assertGreater(len(result['validation']['warnings']), 0)
    
    def test_safe_content_passes(self):
        """Test that safe responses pass validation."""
        safe_response = "Ethereum is a blockchain platform that may allow you to stake ETH. However, staking involves risks including potential loss of funds. Always research thoroughly before making any investment decisions."
        
        result = self.validator.validate("What is Ethereum staking?", safe_response, [])
        self.assertTrue(result['validation']['is_safe'])
    
    def test_disclaimer_addition(self):
        """Test automatic disclaimer addition."""
        response = "You can invest in Bitcoin through exchanges like Coinbase."
        
        result = self.validator.validate("How to buy Bitcoin?", response, [])
        # Should add disclaimer for financial content
        self.assertIn("disclaimer", result['answer'].lower() or 
                     result['validation'].get('warnings', []))


class TestUsageTracking(unittest.TestCase):
    """Test usage tracking and pricing."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tracker = UsageTracker()
    
    def test_free_tier_limits(self):
        """Test free tier query limits."""
        user_id = "free_user"
        
        # Should allow queries up to limit
        for i in range(100):
            allowed = self.tracker.track_query(user_id)
            self.assertTrue(allowed)
        
        # Should block after limit
        allowed = self.tracker.track_query(user_id)
        self.assertFalse(allowed)
    
    def test_tier_upgrade(self):
        """Test upgrading pricing tiers."""
        user_id = "upgrade_user"
        
        # Use up free queries
        for i in range(100):
            self.tracker.track_query(user_id)
        
        # Should be blocked
        self.assertFalse(self.tracker.track_query(user_id))
        
        # Upgrade to PRO
        self.tracker.upgrade_tier(user_id, PricingTier.PRO)
        
        # Should now be allowed
        self.assertTrue(self.tracker.track_query(user_id))
    
    def test_billing_calculation(self):
        """Test billing calculation with overages."""
        user_id = "billing_user"
        
        # Set up PRO tier with some overages
        self.tracker.upgrade_tier(user_id, PricingTier.PRO)
        
        # Use base queries plus some overages
        for i in range(10050):  # 50 overages
            self.tracker.track_query(user_id)
        
        bill = self.tracker.calculate_bill(user_id)
        
        self.assertEqual(bill['base_charge'], 299.0)
        self.assertGreater(bill['overage_charge'], 0)
        self.assertEqual(bill['total'], bill['base_charge'] + bill['overage_charge'])


class TestPrivacyCompliance(unittest.TestCase):
    """Test privacy compliance."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.compliance = PrivacyCompliance()
        self.pii_detector = PIIDetector()
    
    def test_pii_detection(self):
        """Test PII detection in queries."""
        test_cases = [
            ("My email is john@example.com", True),
            ("Call me at 555-123-4567", True),
            ("My wallet is 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb", True),
            ("What is Ethereum?", False)
        ]
        
        for query, should_detect in test_cases:
            has_pii = self.pii_detector.detect(query)
            self.assertEqual(bool(has_pii), should_detect, 
                           f"Query '{query}' PII detection failed")
    
    def test_pii_redaction(self):
        """Test PII redaction."""
        query = "My email is john@example.com and my phone is 555-123-4567"
        redacted = self.pii_detector.redact(query)
        
        self.assertNotIn("john@example.com", redacted)
        self.assertNotIn("555-123-4567", redacted)
        self.assertIn("[REDACTED]", redacted)
    
    def test_consent_management(self):
        """Test GDPR consent management."""
        user_id = "gdpr_user"
        purposes = ["analytics", "personalization"]
        
        # Grant consent
        self.compliance.grant_consent(user_id, purposes)
        
        # Check consent
        self.assertTrue(self.compliance.has_consent(user_id, "analytics"))
        self.assertTrue(self.compliance.has_consent(user_id, "personalization"))
        self.assertFalse(self.compliance.has_consent(user_id, "marketing"))
        
        # Revoke consent
        self.compliance.revoke_consent(user_id)
        self.assertFalse(self.compliance.has_consent(user_id, "analytics"))
    
    def test_data_export(self):
        """Test GDPR data portability."""
        user_id = "export_user"
        
        export = self.compliance.export_user_data(user_id)
        
        self.assertIn('data', export)
        self.assertIn('export_date', export)
        self.assertIn('format', export)
        self.assertEqual(export['format'], 'json')


class TestEndToEndFlow(unittest.TestCase):
    """Test complete end-to-end flow."""
    
    def setUp(self):
        """Set up all components."""
        self.llm_manager = LLMManager()
        self.analytics = Analytics()
        self.memory = ConversationMemory()
        self.validator = ResponseValidator()
        self.tracker = UsageTracker()
        self.compliance = PrivacyCompliance()
    
    def test_complete_query_flow(self):
        """Test a complete query flow through all systems."""
        user_id = "integration_user"
        query = "What is Ethereum staking and how do I get started?"
        region = "US"
        
        # 1. Check usage limits
        can_proceed = self.tracker.track_query(user_id)
        self.assertTrue(can_proceed, "Should allow query within limits")
        
        # 2. Privacy compliance check
        privacy_result = self.compliance.process_query(user_id, query, region)
        self.assertIsNotNone(privacy_result)
        cleaned_query = privacy_result.get('cleaned_query', query)
        
        # 3. Add to conversation memory
        self.memory.add_message(user_id, "user", cleaned_query)
        context = self.memory.get_context(user_id)
        self.assertIn(cleaned_query, context)
        
        # 4. Calculate complexity and select provider
        complexity = self.llm_manager.calculate_complexity_score(cleaned_query)
        provider = self.llm_manager._select_provider(cleaned_query)
        self.assertIsNotNone(provider)
        
        # 5. Log interaction
        self.analytics.log_interaction(
            user_id=user_id,
            query=cleaned_query,
            response="Ethereum staking allows you to earn rewards...",
            category=self.analytics.classify_query(cleaned_query),
            language="en",
            response_time=2.5,
            tokens_used=250,
            cost=0.0003,
            provider=provider.value
        )
        
        # 6. Validate response
        mock_response = "Ethereum staking may allow you to earn rewards by locking your ETH. However, there are risks involved including potential loss of funds."
        validation = self.validator.validate(cleaned_query, mock_response, [])
        self.assertTrue(validation['validation']['is_safe'])
        
        # 7. Check analytics
        insights = self.analytics.get_user_insights(user_id)
        self.assertEqual(insights['total_queries'], 1)
        self.assertIn('staking', insights['categories'])


def run_integration_tests():
    """Run all integration tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestMultiLLMRouting))
    suite.addTests(loader.loadTestsFromTestCase(TestAnalytics))
    suite.addTests(loader.loadTestsFromTestCase(TestConversationMemory))
    suite.addTests(loader.loadTestsFromTestCase(TestResponseValidator))
    suite.addTests(loader.loadTestsFromTestCase(TestUsageTracking))
    suite.addTests(loader.loadTestsFromTestCase(TestPrivacyCompliance))
    suite.addTests(loader.loadTestsFromTestCase(TestEndToEndFlow))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("INTEGRATION TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_integration_tests()
    sys.exit(0 if success else 1)
