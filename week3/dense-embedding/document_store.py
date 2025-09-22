"""In-memory document store for managing documents."""

from typing import Dict, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import uuid
from logger import VectorSearchLogger


@dataclass
class Document:
    """Document data class."""
    id: str
    text: str
    metadata: Dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    embedding: Optional[List[float]] = None


class DocumentStore:
    """In-memory document storage."""
    
    def __init__(self, logger: Optional[VectorSearchLogger] = None):
        """
        Initialize the document store.
        
        Args:
            logger: Logger instance for educational output
        """
        self.documents: Dict[str, Document] = {}
        self.logger = logger
        
        if self.logger:
            self.logger.logger.info("📦 Initialized in-memory document store")
    
    def add_document(self, text: str, doc_id: Optional[str] = None, 
                    metadata: Optional[Dict] = None) -> str:
        """
        Add a document to the store.
        
        Args:
            text: Document text
            doc_id: Optional document ID (will be generated if not provided)
            metadata: Optional metadata dictionary
        
        Returns:
            Document ID
        """
        # Generate ID if not provided
        if doc_id is None:
            doc_id = str(uuid.uuid4())
        
        # Check if document already exists
        if doc_id in self.documents:
            if self.logger:
                self.logger.logger.warning(f"Document {doc_id} already exists, updating...")
        
        # Create document
        doc = Document(
            id=doc_id,
            text=text,
            metadata=metadata or {}
        )
        
        # Store document
        self.documents[doc_id] = doc
        
        if self.logger:
            self.logger.logger.debug(f"📄 Stored document")
            self.logger.logger.debug(f"  - ID: {doc_id}")
            self.logger.logger.debug(f"  - Text length: {len(text)} chars")
            self.logger.logger.debug(f"  - Metadata keys: {list(metadata.keys()) if metadata else []}")
            self.logger.logger.debug(f"  - Total documents: {len(self.documents)}")
        
        return doc_id
    
    def get_document(self, doc_id: str) -> Optional[Document]:
        """
        Retrieve a document by ID.
        
        Args:
            doc_id: Document ID
        
        Returns:
            Document or None if not found
        """
        doc = self.documents.get(doc_id)
        
        if self.logger:
            if doc:
                self.logger.logger.debug(f"✅ Retrieved document {doc_id}")
            else:
                self.logger.logger.warning(f"❌ Document {doc_id} not found")
        
        return doc
    
    def delete_document(self, doc_id: str) -> bool:
        """
        Delete a document from the store.
        
        Args:
            doc_id: Document ID
        
        Returns:
            True if deleted, False if not found
        """
        if doc_id in self.documents:
            del self.documents[doc_id]
            
            if self.logger:
                self.logger.logger.debug(f"🗑️  Deleted document {doc_id}")
                self.logger.logger.debug(f"  Remaining documents: {len(self.documents)}")
            
            return True
        
        if self.logger:
            self.logger.logger.warning(f"Document {doc_id} not found for deletion")
        
        return False
    
    def list_documents(self, limit: Optional[int] = None) -> List[Document]:
        """
        List all documents in the store.
        
        Args:
            limit: Maximum number of documents to return
        
        Returns:
            List of documents
        """
        docs = list(self.documents.values())
        
        if limit:
            docs = docs[:limit]
        
        if self.logger:
            self.logger.logger.debug(f"📋 Listing {len(docs)} documents")
        
        return docs
    
    def get_size(self) -> int:
        """Get the number of documents in the store."""
        return len(self.documents)
    
    def clear(self) -> None:
        """Clear all documents from the store."""
        count = len(self.documents)
        self.documents.clear()
        
        if self.logger:
            self.logger.logger.info(f"🧹 Cleared {count} documents from store")
    
    def get_documents_by_ids(self, doc_ids: List[str]) -> List[Document]:
        """
        Retrieve multiple documents by their IDs.
        
        Args:
            doc_ids: List of document IDs
        
        Returns:
            List of documents (only those found)
        """
        docs = []
        for doc_id in doc_ids:
            doc = self.documents.get(doc_id)
            if doc:
                docs.append(doc)
        
        if self.logger:
            self.logger.logger.debug(f"Retrieved {len(docs)}/{len(doc_ids)} documents")
        
        return docs
    
    def update_document_embedding(self, doc_id: str, embedding: List[float]) -> bool:
        """
        Update the embedding for a document.
        
        Args:
            doc_id: Document ID
            embedding: Embedding vector
        
        Returns:
            True if updated, False if document not found
        """
        if doc_id in self.documents:
            self.documents[doc_id].embedding = embedding
            
            if self.logger:
                self.logger.logger.debug(f"Updated embedding for document {doc_id}")
            
            return True
        
        return False
