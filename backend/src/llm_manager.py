"""
Intelligent LLM Manager with multi-provider support and cost optimization.

Supports OpenAI, Google Gemini, and Perplexity with automatic routing
based on query complexity and cost optimization.
"""

import os
import logging
import time
from typing import Dict, Any, Optional
from enum import Enum

from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Available LLM providers."""
    OPENAI = "openai"
    GEMINI = "gemini"
    PERPLEXITY = "perplexity"
    GROQ = "groq"


class LLMManager:
    """
    Intelligent LLM routing with cost optimization and fallback support.
    
    Routes queries to different LLM providers based on:
    - Query complexity
    - Cost optimization
    - Provider availability
    - Response quality requirements
    """
    
    def __init__(self):
        """Initialize LLM manager with provider configs."""
        self.providers_config = {
            LLMProvider.GEMINI: {
                'cost_per_1m_tokens': 0.0,  # Free tier
                'quality_score': 8,
                'speed_score': 9,
                'available': bool(os.getenv('GOOGLE_API_KEY'))
            },
            LLMProvider.PERPLEXITY: {
                'cost_per_1m_tokens': 0.2,  # Lower cost
                'quality_score': 8,
                'speed_score': 8,
                'available': bool(os.getenv('PERPLEXITY_API_KEY'))
            },
            LLMProvider.OPENAI: {
                'cost_per_1m_tokens': 0.15,  # GPT-4o-mini
                'quality_score': 9,
                'speed_score': 9,
                'available': bool(os.getenv('OPENAI_API_KEY'))
            }
        }
        
        self.query_stats = {
            'total_queries': 0,
            'total_cost': 0.0,
            'provider_usage': {},
            'fallback_count': 0
        }
        
        logger.info("LLM Manager initialized with providers: %s", 
                   [p.value for p, c in self.providers_config.items() if c['available']])
    
    def calculate_complexity_score(self, query: str) -> int:
        """
        Calculate query complexity score (1-10).
        
        Args:
            query: User's query
            
        Returns:
            Complexity score from 1 (simple) to 10 (complex)
        """
        score = 1
        
        # Length-based complexity
        if len(query) > 200:
            score += 2
        elif len(query) > 100:
            score += 1
        
        # Technical terms
        technical_terms = [
            'smart contract', 'defi', 'liquidity pool', 'impermanent loss',
            'yield farming', 'staking rewards', 'gas fees', 'slippage',
            'bridge', 'cross-chain', 'validator', 'consensus'
        ]
        score += sum(1 for term in technical_terms if term in query.lower())
        
        # Question complexity indicators
        complex_indicators = ['how', 'why', 'explain', 'difference', 'compare']
        score += sum(1 for indicator in complex_indicators if indicator in query.lower())
        
        # Multiple questions
        if query.count('?') > 1:
            score += 2
        
        return min(score, 10)
    
    def select_provider(
        self, 
        complexity_score: int,
        prefer_free: bool = True
    ) -> LLMProvider:
        """
        Select the best LLM provider based on complexity and cost.
        
        Args:
            complexity_score: Query complexity (1-10)
            prefer_free: Prefer free providers when possible
            
        Returns:
            Selected LLM provider
        """
        # Simple queries (1-4) -> Use free Gemini
        if complexity_score <= 4 and prefer_free:
            if self.providers_config[LLMProvider.GEMINI]['available']:
                return LLMProvider.GEMINI
        
        # Medium complexity (5-7) -> Use Perplexity or Gemini
        if complexity_score <= 7:
            if self.providers_config[LLMProvider.PERPLEXITY]['available']:
                return LLMProvider.PERPLEXITY
            if self.providers_config[LLMProvider.GEMINI]['available']:
                return LLMProvider.GEMINI
        
        # High complexity (8-10) -> Use OpenAI for best quality
        if self.providers_config[LLMProvider.OPENAI]['available']:
            return LLMProvider.OPENAI
        
        # Fallback to any available provider
        for provider, config in self.providers_config.items():
            if config['available']:
                self.query_stats['fallback_count'] += 1
                logger.warning(f"Using fallback provider: {provider.value}")
                return provider
        
        raise ValueError("No LLM providers available. Please configure API keys.")
    
    def get_llm(self, provider: LLMProvider, temperature: float = 0.3):
        """
        Get LLM instance for the specified provider.
        
        Args:
            provider: LLM provider to use
            temperature: Temperature setting
            
        Returns:
            LLM instance
        """
        if provider == LLMProvider.OPENAI:
            return ChatOpenAI(
                model="gpt-4o-mini",
                temperature=temperature,
                api_key=os.getenv('OPENAI_API_KEY')
            )
        
        elif provider == LLMProvider.GEMINI:
            return ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                temperature=temperature,
                google_api_key=os.getenv('GOOGLE_API_KEY')
            )
        
        elif provider == LLMProvider.PERPLEXITY:
            # Perplexity uses OpenAI-compatible API
            return ChatOpenAI(
                model="llama-3.1-sonar-small-128k-online",
                temperature=temperature,
                api_key=os.getenv('PERPLEXITY_API_KEY'),
                base_url="https://api.perplexity.ai"
            )
        
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def query_with_routing(
        self,
        query: str,
        system_prompt: str,
        prefer_free: bool = True
    ) -> Dict[str, Any]:
        """
        Query LLM with intelligent routing and fallback.
        
        Args:
            query: User's query
            system_prompt: System prompt for context
            prefer_free: Prefer free providers
            
        Returns:
            Response dict with answer and metadata
        """
        start_time = time.time()
        
        # Calculate complexity
        complexity = self.calculate_complexity_score(query)
        
        # Select provider
        provider = self.select_provider(complexity, prefer_free)
        
        logger.info(
            f"Routing query (complexity: {complexity}) to {provider.value}"
        )
        
        # Try primary provider
        try:
            llm = self.get_llm(provider)
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=query)
            ]
            
            response = llm.invoke(messages)
            response_time = time.time() - start_time
            
            # Estimate tokens (rough approximation)
            estimated_tokens = (len(query) + len(response.content)) / 4
            estimated_cost = (estimated_tokens / 1_000_000) * \
                           self.providers_config[provider]['cost_per_1m_tokens']
            
            # Update stats
            self.query_stats['total_queries'] += 1
            self.query_stats['total_cost'] += estimated_cost
            if provider.value not in self.query_stats['provider_usage']:
                self.query_stats['provider_usage'][provider.value] = 0
            self.query_stats['provider_usage'][provider.value] += 1
            
            return {
                'answer': response.content,
                'provider': provider.value,
                'complexity': complexity,
                'response_time': response_time,
                'estimated_tokens': int(estimated_tokens),
                'estimated_cost': estimated_cost,
                'status': 'success'
            }
        
        except Exception as e:
            logger.error(f"Error with {provider.value}: {str(e)}")
            
            # Try fallback providers
            fallback_providers = [
                p for p in self.providers_config.keys() 
                if p != provider and self.providers_config[p]['available']
            ]
            
            for fallback in fallback_providers:
                try:
                    logger.info(f"Trying fallback provider: {fallback.value}")
                    llm = self.get_llm(fallback)
                    messages = [
                        SystemMessage(content=system_prompt),
                        HumanMessage(content=query)
                    ]
                    
                    response = llm.invoke(messages)
                    response_time = time.time() - start_time
                    
                    return {
                        'answer': response.content,
                        'provider': fallback.value,
                        'complexity': complexity,
                        'response_time': response_time,
                        'status': 'success_fallback',
                        'original_provider': provider.value
                    }
                
                except Exception as fallback_error:
                    logger.error(f"Fallback {fallback.value} failed: {fallback_error}")
                    continue
            
            # All providers failed
            return {
                'answer': "I apologize, but I'm experiencing technical difficulties. Please try again in a moment.",
                'provider': 'none',
                'status': 'error',
                'error': str(e)
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        avg_cost_per_query = (
            self.query_stats['total_cost'] / self.query_stats['total_queries']
            if self.query_stats['total_queries'] > 0 else 0
        )
        
        return {
            **self.query_stats,
            'average_cost_per_query': avg_cost_per_query,
            'available_providers': [
                p.value for p, c in self.providers_config.items() 
                if c['available']
            ]
        }


# Global instance
_llm_manager: Optional[LLMManager] = None


def get_llm_manager() -> LLMManager:
    """Get or create global LLM manager instance."""
    global _llm_manager
    if _llm_manager is None:
        _llm_manager = LLMManager()
    return _llm_manager
