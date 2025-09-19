from langchain.embeddings import HuggingFaceEmbeddings
from src.ragService.config.settings import VectorStoreConfig

_embeddings = None

def get_embeddings():
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(model_name=VectorStoreConfig.MODEL_NAME)
    return _embeddings