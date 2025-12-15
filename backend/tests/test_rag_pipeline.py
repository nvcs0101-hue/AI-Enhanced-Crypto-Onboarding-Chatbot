"""
Test suite for the RAG pipeline.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.rag_pipeline import CryptoRAGPipeline, query_rag


@pytest.fixture
def mock_vectorstore():
    """Mock vectorstore for testing."""
    mock = Mock()
    mock.as_retriever.return_value = Mock()
    return mock


@pytest.fixture
def mock_llm():
    """Mock LLM for testing."""
    return Mock()


class TestCryptoRAGPipeline:
    """Test cases for CryptoRAGPipeline class."""
    
    @patch('src.rag_pipeline.HuggingFaceEmbeddings')
    @patch('src.rag_pipeline.Chroma')
    @patch('src.rag_pipeline.ChatOpenAI')
    def test_initialization(self, mock_openai, mock_chroma, mock_embeddings):
        """Test pipeline initialization."""
        pipeline = CryptoRAGPipeline()
        
        assert pipeline is not None
        assert mock_embeddings.called
        assert mock_chroma.called
        assert mock_openai.called
    
    @patch('src.rag_pipeline.CryptoRAGPipeline._initialize_qa_chain')
    @patch('src.rag_pipeline.CryptoRAGPipeline._initialize_llm')
    @patch('src.rag_pipeline.CryptoRAGPipeline._initialize_vectorstore')
    @patch('src.rag_pipeline.CryptoRAGPipeline._initialize_embeddings')
    def test_query_success(self, mock_emb, mock_vs, mock_llm, mock_qa):
        """Test successful query processing."""
        # Mock the QA chain response
        mock_qa_chain = Mock()
        mock_qa_chain.invoke.return_value = {
            'result': 'Test answer',
            'source_documents': []
        }
        
        with patch.object(CryptoRAGPipeline, 'qa_chain', mock_qa_chain):
            pipeline = CryptoRAGPipeline()
            response = pipeline.query("Test question")
            
            assert response['status'] == 'success'
            assert 'answer' in response
    
    def test_query_with_sources(self):
        """Test query with source documents."""
        with patch('src.rag_pipeline.get_pipeline') as mock_get:
            mock_pipeline = Mock()
            mock_pipeline.query.return_value = {
                'answer': 'Test answer',
                'status': 'success',
                'sources': []
            }
            mock_get.return_value = mock_pipeline
            
            response = query_rag("Test", return_sources=True)
            assert 'sources' in response or response['status'] == 'success'


class TestQueryRagFunction:
    """Test cases for query_rag convenience function."""
    
    def test_query_rag_basic(self):
        """Test basic query_rag functionality."""
        with patch('src.rag_pipeline.get_pipeline') as mock_get:
            mock_pipeline = Mock()
            mock_pipeline.query.return_value = {
                'answer': 'Test answer',
                'status': 'success'
            }
            mock_get.return_value = mock_pipeline
            
            response = query_rag("How do I stake ETH?")
            assert response['status'] == 'success'
            assert 'answer' in response
    
    def test_query_rag_with_language(self):
        """Test query_rag with language parameter."""
        with patch('src.rag_pipeline.get_pipeline') as mock_get:
            mock_pipeline = Mock()
            mock_pipeline.query.return_value = {
                'answer': 'Test answer',
                'status': 'success'
            }
            mock_get.return_value = mock_pipeline
            
            response = query_rag("Test", language="Spanish")
            mock_pipeline.query.assert_called_with("Test", "Spanish", False)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
