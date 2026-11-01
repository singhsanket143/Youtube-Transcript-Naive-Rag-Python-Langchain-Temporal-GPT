from app.services.strategies.pdf_loader_strategy import PdfLoaderStrategy
from app.services.strategies.csv_loader_strategy import CsvLoaderStrategy
from app.services.strategies.document_loader_strategy import DocumentLoaderStrategy
from pathlib import Path


class DocumentLoaderFactory:
    """Factory for creating document loaders based on extension type."""

    SUPPORTED_FILE_EXTENSIONS = {".csv"}

    @staticmethod
    def get_loader(file_path: Path) -> DocumentLoaderStrategy:
        file_path = Path(file_path)

        # Getting the document extension type (.csv, .txt, .pdf, etc)
        file_extension = file_path.suffix.lower()

        if file_extension not in DocumentLoaderFactory.SUPPORTED_FILE_EXTENSIONS:
            raise ValueError(f"Unsupported file extension: {file_extension}")

        if file_extension == ".csv":
            return CsvLoaderStrategy()
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
