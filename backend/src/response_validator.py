"""
Response validation to ensure accuracy and safety.

Validates LLM responses for quality, accuracy, and safety before delivery.
"""

import logging
import re
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class ResponseValidator:
    """
    Validate LLM responses for quality, accuracy, and safety.
    
    Features:
    - Source citation verification
    - Dangerous content detection
    - Contradiction checking
    - Confidence scoring
    - Disclaimer addition
    """
    
    def __init__(self):
        """Initialize response validator."""
        # Dangerous phrases that should trigger warnings
        self.dangerous_phrases = [
            'guaranteed returns',
            'guaranteed profit',
            'no risk',
            'risk-free',
            'definitely safe',
            'can\'t lose',
            'cannot lose',
            '100% safe',
            'zero risk',
            'free money',
            'get rich quick'
        ]
        
        # Financial advice phrases
        self.financial_advice_phrases = [
            'you should invest',
            'i recommend investing',
            'buy this token',
            'sell your',
            'you should buy',
            'you should sell'
        ]
        
        # Phrases requiring disclaimers
        self.disclaimer_triggers = [
            'invest', 'trading', 'profit', 'returns', 'gains',
            'financial', 'money', 'price', 'value'
        ]
        
        logger.info("Response validator initialized")
    
    def validate(
        self,
        response: str,
        query: str,
        source_documents: Optional[List] = None
    ) -> Dict[str, any]:
        """
        Comprehensive validation of response.
        
        Args:
            response: LLM response to validate
            query: Original user query
            source_documents: Retrieved source documents
            
        Returns:
            Validation results with modified response if needed
        """
        validation_result = {
            'original_response': response,
            'modified_response': response,
            'is_safe': True,
            'needs_disclaimer': False,
            'confidence_score': 1.0,
            'warnings': [],
            'modifications': []
        }
        
        # Check for dangerous financial claims
        dangerous_found = self._check_dangerous_content(response)
        if dangerous_found:
            validation_result['is_safe'] = False
            validation_result['warnings'].extend(dangerous_found)
            validation_result['modified_response'] = self._tone_down_response(
                response, dangerous_found
            )
            validation_result['modifications'].append('toned_down_dangerous_claims')
        
        # Check for financial advice
        advice_found = self._check_financial_advice(response)
        if advice_found:
            validation_result['warnings'].append('contains_financial_advice')
            validation_result['needs_disclaimer'] = True
        
        # Check if disclaimer is needed
        if self._needs_disclaimer(response):
            validation_result['needs_disclaimer'] = True
            validation_result['modified_response'] = self._add_disclaimer(
                validation_result['modified_response']
            )
            validation_result['modifications'].append('added_disclaimer')
        
        # Check response length and quality
        quality_score = self._assess_quality(response, query)
        validation_result['quality_score'] = quality_score
        
        if quality_score < 0.5:
            validation_result['warnings'].append('low_quality_response')
        
        # Verify source citations if documents provided
        if source_documents:
            citation_score = self._verify_citations(response, source_documents)
            validation_result['citation_score'] = citation_score
            
            if citation_score < 0.3:
                validation_result['warnings'].append('weak_source_attribution')
                validation_result['confidence_score'] *= 0.8
        
        # Check for contradictions
        if self._contains_contradictions(response):
            validation_result['warnings'].append('potential_contradictions')
            validation_result['confidence_score'] *= 0.7
        
        return validation_result
    
    def _check_dangerous_content(self, response: str) -> List[str]:
        """Check for dangerous financial claims."""
        found = []
        response_lower = response.lower()
        
        for phrase in self.dangerous_phrases:
            if phrase in response_lower:
                found.append(f"dangerous_claim: {phrase}")
                logger.warning(f"Dangerous phrase found: {phrase}")
        
        return found
    
    def _check_financial_advice(self, response: str) -> List[str]:
        """Check for direct financial advice."""
        found = []
        response_lower = response.lower()
        
        for phrase in self.financial_advice_phrases:
            if phrase in response_lower:
                found.append(f"financial_advice: {phrase}")
                logger.warning(f"Financial advice phrase found: {phrase}")
        
        return found
    
    def _needs_disclaimer(self, response: str) -> bool:
        """Check if response needs a disclaimer."""
        response_lower = response.lower()
        return any(
            trigger in response_lower 
            for trigger in self.disclaimer_triggers
        )
    
    def _add_disclaimer(self, response: str) -> str:
        """Add disclaimer to response."""
        disclaimer = (
            "\n\n⚠️ **Disclaimer:** This information is for educational purposes only "
            "and should not be considered financial advice. Always do your own research "
            "and consult with a qualified financial advisor before making investment decisions."
        )
        
        return response + disclaimer
    
    def _tone_down_response(
        self,
        response: str,
        dangerous_phrases: List[str]
    ) -> str:
        """Tone down dangerous claims in response."""
        modified = response
        
        # Replace absolute claims with more cautious language
        replacements = {
            'guaranteed': 'potentially possible',
            'definitely': 'possibly',
            'always': 'often',
            'never': 'rarely',
            '100%': 'high',
            'risk-free': 'lower risk',
            'no risk': 'reduced risk',
            'can\'t lose': 'lower risk of loss',
            'cannot lose': 'lower risk of loss'
        }
        
        for original, replacement in replacements.items():
            pattern = re.compile(re.escape(original), re.IGNORECASE)
            modified = pattern.sub(replacement, modified)
        
        logger.info("Toned down dangerous claims in response")
        return modified
    
    def _assess_quality(self, response: str, query: str) -> float:
        """
        Assess response quality.
        
        Returns:
            Quality score from 0.0 to 1.0
        """
        score = 1.0
        
        # Check response length
        if len(response) < 50:
            score *= 0.7  # Too short
        elif len(response) > 2000:
            score *= 0.9  # Very long, might be rambling
        
        # Check if response addresses the query
        query_words = set(query.lower().split())
        response_words = set(response.lower().split())
        overlap = len(query_words & response_words)
        
        if overlap < len(query_words) * 0.2:
            score *= 0.8  # Low relevance
        
        # Check for structure (paragraphs, lists)
        has_structure = '\n' in response or any(
            marker in response for marker in ['1.', '2.', '•', '-']
        )
        if not has_structure and len(response) > 300:
            score *= 0.9
        
        return round(score, 2)
    
    def _verify_citations(
        self,
        response: str,
        source_documents: List
    ) -> float:
        """
        Verify that response is grounded in source documents.
        
        Returns:
            Citation score from 0.0 to 1.0
        """
        if not source_documents:
            return 0.5  # Neutral if no sources
        
        # Extract key phrases from response (simple approach)
        response_sentences = response.split('.')
        
        # Check how many sentences can be found in sources
        grounded_sentences = 0
        
        for sentence in response_sentences:
            if len(sentence.strip()) < 20:
                continue
            
            # Check if sentence content appears in any source
            for doc in source_documents:
                doc_content = doc.page_content if hasattr(doc, 'page_content') else str(doc)
                if any(
                    word in doc_content.lower() 
                    for word in sentence.lower().split() 
                    if len(word) > 4
                ):
                    grounded_sentences += 1
                    break
        
        total_sentences = len([s for s in response_sentences if len(s.strip()) > 20])
        
        if total_sentences == 0:
            return 0.5
        
        return round(grounded_sentences / total_sentences, 2)
    
    def _contains_contradictions(self, response: str) -> bool:
        """
        Check for potential contradictions in response.
        
        Simple heuristic: look for contradictory phrases.
        """
        contradictory_pairs = [
            (['always', 'never'], ['sometimes', 'occasionally']),
            (['safe', 'secure'], ['risky', 'dangerous', 'unsafe']),
            (['recommended', 'should'], ['not recommended', 'should not']),
            (['increase', 'gain'], ['decrease', 'loss']),
        ]
        
        response_lower = response.lower()
        
        for positive_words, negative_words in contradictory_pairs:
            has_positive = any(word in response_lower for word in positive_words)
            has_negative = any(word in response_lower for word in negative_words)
            
            if has_positive and has_negative:
                logger.warning("Potential contradiction detected in response")
                return True
        
        return False


# Global validator instance
_validator: Optional[ResponseValidator] = None


def get_validator() -> ResponseValidator:
    """Get or create global response validator instance."""
    global _validator
    if _validator is None:
        _validator = ResponseValidator()
    return _validator
