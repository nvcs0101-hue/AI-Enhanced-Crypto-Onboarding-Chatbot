"""
RAG (Retrieval-Augmented Generation) pipeline for the crypto onboarding chatbot.

This module handles querying the vector database, retrieving relevant context,
and generating responses using LLMs with advanced features:
- Multi-LLM provider support with intelligent routing
- Analytics tracking
- Response validation
- Conversation memory
"""

from typing import Optional, Dict, Any, List
import logging
import os
import time
from pathlib import Path

from langchain_chroma import Chroma
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
from langchain_core.documents import Document

from src.llm_manager import get_llm_manager
from src.analytics import get_analytics
from src.response_validator import get_validator
from src.conversation_memory import get_conversation_memory

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CryptoRAGPipeline:
    """RAG pipeline for handling crypto onboarding queries."""
    
    def __init__(
        self,
        persist_directory: str = "./chroma_db",
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        llm_model: str = "gpt-4o-mini",
        llm_temperature: float = 0.3,
        retrieval_k: int = 4
    ):
        """
        Initialize the RAG pipeline.
        
        Args:
            persist_directory: Path to the Chroma vector database
            embedding_model: HuggingFace embedding model name
            llm_model: OpenAI model name
            llm_temperature: LLM temperature setting
            retrieval_k: Number of documents to retrieve
        """
        self.persist_directory = persist_directory
        self.embedding_model = embedding_model
        self.llm_model = llm_model
        self.llm_temperature = llm_temperature
        self.retrieval_k = retrieval_k
        
        # Initialize components
        self._initialize_embeddings()
        self._initialize_vectorstore()
        self._initialize_llm()
        self._initialize_qa_chain()
        
    def _initialize_embeddings(self) -> None:
        """Initialize the embeddings model."""
        logger.info(f"Initializing embeddings with model: {self.embedding_model}")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=self.embedding_model
        )
        
    def _initialize_vectorstore(self) -> None:
        """Initialize the vector store."""
        try:
            if not Path(self.persist_directory).exists():
                raise FileNotFoundError(
                    f"Vector store not found at {self.persist_directory}. "
                    "Please build the knowledge base first using build_knowledge_base.py"
                )
            
            logger.info(f"Loading vector store from {self.persist_directory}")
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
            
            # Create retriever
            self.retriever = self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": self.retrieval_k}
            )
            
            logger.info("Vector store retriever initialized")
            
        except Exception as e:
            logger.error(f"Failed to load vector store: {e}")
            raise
    
    def _initialize_llm(self):
        """Initialize LLM manager with multi-provider support."""
        try:
            # Use LLM manager instead of single provider
            self.llm_manager = get_llm_manager()
            self.analytics = get_analytics()
            self.validator = get_validator()
            self.conversation_memory = get_conversation_memory()
            
            logger.info("Initialized RAG pipeline with multi-LLM support")
            
        except Exception as e:
            logger.error(f"Error initializing LLM manager: {str(e)}")
            raise
    
    def _create_prompt_template(self) -> PromptTemplate:
        """
        Create the prompt template for the QA chain.
        
        Returns:
            PromptTemplate instance
        """
        template = """You are a helpful and knowledgeable crypto onboarding assistant. Your role is to guide users through cryptocurrency concepts, staking, bridging, wallet setup, and protocol navigation.

Use the following context from the documentation to answer the user's question. If the answer is not in the context, use your knowledge but clearly indicate you're providing general information.

Context from documentation:
{context}

Question: {question}

Language: Answer in {language}

Instructions:
- Be clear, concise, and beginner-friendly
- Use step-by-step explanations for processes
- Highlight security considerations when relevant
- If you do not know something, say so honestly
- Format your response with markdown for readability

Answer:"""
        
        return PromptTemplate(
            template=template,
            input_variables=["context", "question", "language"]
        )
     components."""
        logger.info("QA chain initialization complete - using dynamic LLM routing"    return_source_documents=True,
            chain_type_kwargs={"prompt": prompt}
        )
    
    def query(
        self,
        question: str,
        language: str = "English",
        return_sources: bool = False
    ) -> Dict[str, Any]:
        """
        Query the RAG pipeline.
        
        Args:
            question: User's question
            language: Language for the response
            return_sources: Whether ,
        user_id: str = "anonymous"
    ) -> Dict[str, Any]:
        """
        Query the RAG pipeline with advanced features.
        
        Args:
            question: User's question
            language: Language for the response
            return_sources: Whether to return source documents
            user_id: User identifier for conversation memory
            
        Returns:
            Dictionary containing response and metadata
        """
        start_time = time.time()
        
        try:
            logger.info(f"Processing query: {question[:100]}...")
            
            # Get conversation context
            conversation_context = self.conversation_memory.get_context(user_id)
            
            # Retrieve relevant documents
            docs = self.retriever.get_relevant_documents(question)
            
            # Build context from retrieved documents
            context = "\n\n".join([doc.page_content for doc in docs[:4]])
            
            # Create enhanced prompt
            system_prompt = f"""You are a helpful and knowledgeable crypto onboarding assistant.
Your role is to guide users through cryptocurrency concepts, staking, bridging, wallet setup, and protocol navigation.

{f"Previous conversation:{conversation_context}" if conversation_context else ""}

Use the following context from the documentation to answer the user's question in {language}.
If the answer is not in the context, use your knowledge but clearly indicate you're providing general information.

Context from documentation:
{context}

Instructions:
- Be clear, concise, and beginner-friendly
- Use step-by-step explanations for processes
- Highlight security considerations when relevant
- If you do not know something, say so honestly
- Format your response with markdown for readability
- Never make guarantees about financial returns or safety"""
            
            # Query LLM with intelligent routing
            llm_result = self.llm_manager.query_with_routing(
                query=question,
                system_prompt=system_prompt,
                prefer_free=True
            )
            
            # Validate response
            validation = self.validator.validate(
                response=llm_result['answer'],
                query=question,
                source_documents=docs
            )
            
            # Use modified response if validation changed it
            final_answer = validation['modified_response']
            
            # Calculate metrics
            response_time = time.time() - start_time
            
            # Log to analytics
            self.analytics.log_interaction(
                user_id=user_id,,
    user_id: str = "anonymous"
) -> Dict[str, Any]:
    """
    Convenience function to query the RAG pipeline.
    
    Args:
        user_question: User's question
        language: Language for the response
        return_sources: Whether to return source documents
        user_id: User identifier for conversation memory
        
    Returns:
        Dictionary containing response and metadata
    """
    pipeline = get_pipeline()
    return pipeline.query(user_question, language, return_sources, user_id
            
            # Add to conversation memory
            self.conversation_memory.add_message(user_id, 'user', question)
            self.conversation_memory.add_message(user_id, 'assistant', final_answer)
            
            # Build response
            response = {
                "answer": final_answer,
                "status": "success",
                "provider": llm_result.get('provider'),
                "response_time": round(response_time, 3),
                "validation": {
                    "confidence_score": validation.get('confidence_score', 1.0),
                    "warnings": validation.get('warnings', [])
                }
            }
            
            if return_sources:
                sources = []
                for doc in docs[:4]:
                    sources.append({
                        "content": doc.page_content[:500],
                        "metadata": doc.metadata
                    })
                response["sources"] = sources
            
            logger.info(
                f"Query processed successfully via {llm_result.get('provider')} "
                f"in {response_time:.2f}s"
            )
            return response
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}", exc_info=True)
            
            # Log error to analytics
            self.analytics.log_interaction(
                user_id=user_id,
                query=question,
                response="Error",
                response_time=time.time() - start_time,
                tokens_used=0,
                estimated_cost=0.0,
                language=language,
                provider='none',
                status='error',
                metadata={'error': str(e)}
            )
            
_pipeline_instance: Optional[CryptoRAGPipeline] = None


def get_pipeline() -> CryptoRAGPipeline:
    """
    Get or create the global RAG pipeline instance.
    
    Returns:
        CryptoRAGPipeline instance
    """
    global _pipeline_instance
    
    if _pipeline_instance is None:
        logger.info("Creating new RAG pipeline instance")
        _pipeline_instance = CryptoRAGPipeline()
    
    return _pipeline_instance


def query_rag(
    user_question: str,
    language: str = "English",
    return_sources: bool = False
) -> Dict[str, Any]:
    """
    Convenience function to query the RAG pipeline.
    
    Args:
        user_question: User's question
        language: Language for the response
        return_sources: Whether to return source documents
        
    Returns:
        Dictionary containing response and optional source documents
    """
    pipeline = get_pipeline()
    return pipeline.query(user_question, language, return_sources)


if __name__ == "__main__":
    """Test the RAG pipeline."""
    import sys
    
    # Check if OPENAI_API_KEY is set
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY not set. Please set it before testing.")
        sys.exit(1)
    
    # Test query
    test_question = "How do I set up a MetaMask wallet?"
    logger.info(f"Testing with question: {test_question}")
    
    try:
        response = query_rag(test_question, return_sources=True)
        print("\n" + "="*50)
        print("ANSWER:")
        print("="*50)
        print(response["answer"])
        
        if "sources" in response:
            print("\n" + "="*50)
            print("SOURCES:")
            print("="*50)
            for i, source in enumerate(response["sources"], 1):
                print(f"\nSource {i}:")
                print(source["content"][:200] + "...")
    
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        sys.exit(1)
