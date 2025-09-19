import os
from typing import List
from langchain.schema import Document
from langchain.vectorstores import FAISS

from src.ragService.config.settings import VectorStoreConfig
from src.ragService.vector_store.embeddings import get_embeddings


def create_vector_store(documents: List[Document]) -> bool:
    if not documents:
        return False

    try:
        embeddings = get_embeddings()
        vectorstore = FAISS.from_documents(documents, embeddings)
        vectorstore.save_local(VectorStoreConfig.PATH)
        return True
    except Exception as e:
        print(f"Ошибка создания векторного хранилища: {e}")
        return False


def load_vector_store():
    if not os.path.exists(VectorStoreConfig.PATH):
        return None

    try:
        embeddings = get_embeddings()
        return FAISS.load_local(
            VectorStoreConfig.PATH,
            embeddings,
            allow_dangerous_deserialization=True
        )
    except Exception as e:
        print(f"Ошибка загрузки векторного хранилища: {e}")
        return None