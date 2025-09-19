import os
from dotenv import load_dotenv
from dataclasses import dataclass

load_dotenv()


@dataclass
class S3Config:
    ENDPOINT: str = os.getenv('S3_ENDPOINT', 'https://storage.yandexcloud.net')
    ACCESS_KEY: str = os.getenv('S3_ACCESS_KEY')
    SECRET_KEY: str = os.getenv('S3_SECRET_KEY')
    BUCKET: str = os.getenv('S3_BUCKET', 'rag-docs-trusted')
    REGION: str = os.getenv('S3_REGION', 'ru-central1')
    PREFIX: str = os.getenv('S3_PREFIX', '')  # <-- добавлено, по умолчанию пустая строка


@dataclass
class VectorStoreConfig:
    PATH: str = os.getenv('VECTOR_STORE_PATH', './vectorstore_faiss')
    CHUNK_SIZE: int = int(os.getenv('CHUNK_SIZE', '500'))
    CHUNK_OVERLAP: int = int(os.getenv('CHUNK_OVERLAP', '50'))
    MODEL_NAME: str = os.getenv('EMBEDDINGS_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')


@dataclass
class RetrieverConfig:
    SEARCH_K: int = int(os.getenv('SEARCH_K', '3'))
    SIMILARITY_THRESHOLD: float = float(os.getenv('SIMILARITY_THRESHOLD', '0.7'))
    MAX_FILE_SIZE: int = int(os.getenv('MAX_FILE_SIZE', '52428800'))  # 50MB


def validate_config():
    """Проверка всех обязательных переменных окружения"""
    required_vars = [
        'S3_ACCESS_KEY',
        'S3_SECRET_KEY',
        'S3_BUCKET',
        'VECTOR_STORE_PATH',
    ]
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

    # Можно добавить предупреждение, если PREFIX пустой
    if not os.getenv('S3_PREFIX'):
        print("Предупреждение: S3_PREFIX пустой, будут загружаться все объекты из бакета.")
