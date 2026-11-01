from langchain_core.documents import Document
from app.configs.settings import Settings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.services.factories.document_loader_factory import DocumentLoaderFactory
from pathlib import Path

from app.utils import get_logger

logger = get_logger(__name__)

class DocumentService:
    """Service for document processing."""

    def __init__(self, chunk_size: int | None = None, chunk_overlap: int | None = None):
        settings = Settings()
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", " ", ""],
            length_function=len,
        )

    def load_file(self, file_path: Path, source_name: str | None = None) -> list[Document]:
        """Load a file into a list of Documents using the appropriate loader strategy."""
        document_loader = DocumentLoaderFactory.get_loader(file_path=file_path)
        documents = document_loader.load(file_path=file_path, source_name=source_name)

        logger.info(f"Loaded {len(documents)} documents from {file_path}")
        return documents

    def split_documents(self, documents: list[Document]) -> list[Document]:
        """Split documents into chunks."""
        return self.text_splitter.split_documents(documents)

    def process_file(self, file_path: Path, source_name: str | None = None) -> list[Document]:
        """Load and split a file into chunked Documents."""
        documents = self.load_file(file_path, source_name)
        return self.split_documents(documents)
