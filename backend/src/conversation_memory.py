"""
Conversation memory management for multi-turn conversations.

Maintains context across messages for better UX with follow-up questions.
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import deque
import hashlib

logger = logging.getLogger(__name__)


class ConversationMemory:
    """
    Maintain conversation context for multi-turn interactions.
    
    Features:
    - Per-user conversation history
    - Automatic expiration of old conversations
    - Context summarization for long conversations
    - Memory-efficient storage with limits
    """
    
    def __init__(
        self,
        max_history: int = 10,
        ttl_minutes: int = 30,
        max_context_tokens: int = 2000
    ):
        """
        Initialize conversation memory.
        
        Args:
            max_history: Maximum messages to store per conversation
            ttl_minutes: Time-to-live for inactive conversations
            max_context_tokens: Maximum tokens for context
        """
        self.conversations: Dict[str, Dict] = {}
        self.max_history = max_history
        self.ttl = timedelta(minutes=ttl_minutes)
        self.max_context_tokens = max_context_tokens
        
        logger.info(
            f"Conversation memory initialized: "
            f"max_history={max_history}, ttl={ttl_minutes}min"
        )
    
    def add_message(
        self,
        user_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict] = None
    ) -> None:
        """
        Add a message to conversation history.
        
        Args:
            user_id: User identifier
            role: Message role ('user' or 'assistant')
            content: Message content
            metadata: Optional metadata
        """
        if user_id not in self.conversations:
            self.conversations[user_id] = {
                'messages': deque(maxlen=self.max_history),
                'created_at': datetime.utcnow(),
                'last_active': datetime.utcnow(),
                'message_count': 0
            }
        
        conversation = self.conversations[user_id]
        
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.utcnow(),
            'metadata': metadata or {}
        }
        
        conversation['messages'].append(message)
        conversation['last_active'] = datetime.utcnow()
        conversation['message_count'] += 1
        
        logger.debug(
            f"Added {role} message to conversation {user_id[:8]} "
            f"(total: {len(conversation['messages'])})"
        )
    
    def get_context(
        self,
        user_id: str,
        include_system_prompt: bool = True
    ) -> str:
        """
        Get conversation context for RAG queries.
        
        Args:
            user_id: User identifier
            include_system_prompt: Include system prompt in context
            
        Returns:
            Formatted conversation context
        """
        if user_id not in self.conversations:
            return ""
        
        conversation = self.conversations[user_id]
        
        # Check if conversation has expired
        if datetime.utcnow() - conversation['last_active'] > self.ttl:
            logger.info(f"Conversation {user_id[:8]} expired, clearing")
            del self.conversations[user_id]
            return ""
        
        # Build context from messages
        context_parts = []
        
        if include_system_prompt:
            context_parts.append(
                "Previous conversation context (for reference):\n"
            )
        
        for msg in conversation['messages']:
            role_label = "User" if msg['role'] == 'user' else "Assistant"
            context_parts.append(f"{role_label}: {msg['content']}")
        
        context = "\n".join(context_parts)
        
        # Truncate if too long (rough token estimation: 1 token ≈ 4 chars)
        max_chars = self.max_context_tokens * 4
        if len(context) > max_chars:
            context = context[-max_chars:]
            logger.debug(f"Truncated context for {user_id[:8]} to fit token limit")
        
        return context
    
    def get_messages(self, user_id: str) -> List[Dict]:
        """
        Get all messages for a conversation.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of message dictionaries
        """
        if user_id not in self.conversations:
            return []
        
        return list(self.conversations[user_id]['messages'])
    
    def clear_conversation(self, user_id: str) -> bool:
        """
        Clear conversation history for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if conversation was cleared, False if not found
        """
        if user_id in self.conversations:
            del self.conversations[user_id]
            logger.info(f"Cleared conversation for {user_id[:8]}")
            return True
        return False
    
    def cleanup_expired(self) -> int:
        """
        Remove expired conversations.
        
        Returns:
            Number of conversations removed
        """
        now = datetime.utcnow()
        expired_users = [
            user_id for user_id, conv in self.conversations.items()
            if now - conv['last_active'] > self.ttl
        ]
        
        for user_id in expired_users:
            del self.conversations[user_id]
        
        if expired_users:
            logger.info(f"Cleaned up {len(expired_users)} expired conversations")
        
        return len(expired_users)
    
    def get_conversation_stats(self, user_id: str) -> Optional[Dict]:
        """
        Get statistics for a conversation.
        
        Args:
            user_id: User identifier
            
        Returns:
            Conversation statistics or None if not found
        """
        if user_id not in self.conversations:
            return None
        
        conversation = self.conversations[user_id]
        duration = datetime.utcnow() - conversation['created_at']
        
        return {
            'message_count': conversation['message_count'],
            'messages_in_memory': len(conversation['messages']),
            'created_at': conversation['created_at'].isoformat(),
            'last_active': conversation['last_active'].isoformat(),
            'duration_minutes': round(duration.total_seconds() / 60, 2),
            'is_active': datetime.utcnow() - conversation['last_active'] < self.ttl
        }
    
    def get_all_stats(self) -> Dict:
        """
        Get statistics for all conversations.
        
        Returns:
            Global conversation statistics
        """
        active_conversations = sum(
            1 for conv in self.conversations.values()
            if datetime.utcnow() - conv['last_active'] < self.ttl
        )
        
        total_messages = sum(
            conv['message_count'] for conv in self.conversations.values()
        )
        
        return {
            'total_conversations': len(self.conversations),
            'active_conversations': active_conversations,
            'total_messages': total_messages,
            'average_messages_per_conversation': (
                round(total_messages / len(self.conversations), 2)
                if self.conversations else 0
            )
        }


# Global conversation memory instance
_conversation_memory: Optional[ConversationMemory] = None


def get_conversation_memory() -> ConversationMemory:
    """Get or create global conversation memory instance."""
    global _conversation_memory
    if _conversation_memory is None:
        _conversation_memory = ConversationMemory()
    return _conversation_memory
