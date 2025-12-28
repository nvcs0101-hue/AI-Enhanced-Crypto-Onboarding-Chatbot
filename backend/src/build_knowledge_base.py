"""
Build and maintain the RAG knowledge base from crypto project documentation.

This module handles document loading, chunking, embedding, and vector store creation
for the crypto onboarding chatbot's knowledge base.
"""

from typing import Optional, List
import logging
from pathlib import Path

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class KnowledgeBaseBuilder:
    """Handles the creation and management of the vector knowledge base."""
    
    def __init__(
        self,
        docs_directory: str = "data/docs/",
        persist_directory: str = "./chroma_db",
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ):
        """
        Initialize the knowledge base builder.
        
        Args:
            docs_directory: Path to directory containing documentation files
            persist_directory: Path to persist the Chroma vector database
            embedding_model: HuggingFace embedding model name
            chunk_size: Size of text chunks for splitting
            chunk_overlap: Overlap between chunks
        """
        self.docs_directory = Path(docs_directory)
        self.persist_directory = persist_directory
        self.embedding_model = embedding_model
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Initialize embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name=self.embedding_model
        )
        
    def load_documents(self) -> List[Document]:
        """
        Load documents from the docs directory.
        
        Returns:
            List of loaded Document objects
            
        Raises:
            FileNotFoundError: If docs directory doesn't exist
            ValueError: If no documents found
        """
        if not self.docs_directory.exists():
            raise FileNotFoundError(
                f"Documentation directory not found: {self.docs_directory}"
            )
        
        logger.info(f"Loading documents from {self.docs_directory}")
        
        # Load markdown files
        try:
            loader = DirectoryLoader(
                str(self.docs_directory),
                glob="**/*.md",
                loader_cls=TextLoader,
                show_progress=True
            )
            documents = loader.load()
            
            if not documents:
                raise ValueError(
                    f"No documents found in {self.docs_directory}. "
                    "Please add markdown files to the docs directory."
                )
            
            logger.info(f"Successfully loaded {len(documents)} documents")
            return documents
            
        except Exception as e:
            logger.error(f"Error loading documents: {str(e)}")
            raise
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into chunks.
        
        Args:
            documents: List of Document objects to split
            
        Returns:
            List of chunked Document objects
        """
        logger.info("Splitting documents into chunks")
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        chunks = text_splitter.split_documents(documents)
        logger.info(f"Created {len(chunks)} chunks from {len(documents)} documents")
        
        return chunks
    
    def create_vector_store(self, chunks: List[Document]) -> Chroma:
        """
        Create and persist a Chroma vector store from document chunks.
        
        Args:
            chunks: List of document chunks to embed
            
        Returns:
            Chroma vector store instance
        """
        logger.info("Creating vector store with embeddings")
        
        try:
            vectorstore = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                persist_directory=self.persist_directory
            )
            
            logger.info(
                f"Vector store created successfully at {self.persist_directory}"
            )
            return vectorstore
            
        except Exception as e:
            logger.error(f"Error creating vector store: {str(e)}")
            raise
    
    def build(self) -> Chroma:
        """
        Build the complete knowledge base pipeline.
        
        Returns:
            Chroma vector store instance
        """
        logger.info("Starting knowledge base build process")
        
        # Load documents
        documents = self.load_documents()
        
        # Split into chunks
        chunks = self.split_documents(documents)
        
        # Create vector store
        vectorstore = self.create_vector_store(chunks)
        
        logger.info("Knowledge base build completed successfully")
        return vectorstore


def build_vector_db(
    docs_directory: str = "data/docs/",
    persist_directory: str = "./chroma_db"
) -> Chroma:
    """
    Convenience function to build the vector database.
    
    Args:
        docs_directory: Path to documentation directory
        persist_directory: Path to persist vector database
        
    Returns:
        Chroma vector store instance
    """
    builder = KnowledgeBaseBuilder(
        docs_directory=docs_directory,
        persist_directory=persist_directory
    )
    return builder.build()


if __name__ == "__main__":
    """Build the knowledge base when run as a script."""
    try:
        # Create sample documentation if none exists
        docs_path = Path("data/docs")
        docs_path.mkdir(parents=True, exist_ok=True)
        
        sample_doc = docs_path / "sample_crypto_guide.md"
        if not sample_doc.exists():
            logger.info("Creating sample documentation")
            sample_doc.write_text("""# Crypto Onboarding Guide

## What is Staking?

Staking is the process of locking up your cryptocurrency to support a blockchain network's operations. In return, you earn rewards, similar to earning interest on a savings account.

### How to Stake

1. Choose a staking platform or validator
2. Transfer your tokens to a staking wallet
3. Delegate your tokens to a validator
4. Start earning staking rewards

## What is Bridging?

Bridging allows you to transfer assets between different blockchain networks. It's essential for cross-chain interoperability.

### Popular Bridges

- Multichain Bridge
- Wormhole
- Synapse Protocol

## Wallet Setup

### MetaMask Setup

1. Install MetaMask browser extension
2. Create a new wallet
3. Save your seed phrase securely
4. Add custom networks if needed

### Hardware Wallets

For maximum security, consider using:
- Ledger Nano X
- Trezor Model T

## Security Best Practices

- Never share your seed phrase
- Use hardware wallets for large amounts
- Enable 2FA where possible
- Verify contract addresses before interacting
""")
        
        # Build the knowledge base
        vectorstore = build_vector_db()
        logger.info("Knowledge base ready for queries")
        
    except Exception as e:
        logger.error(f"Failed to build knowledge base: {str(e)}")
        raise
