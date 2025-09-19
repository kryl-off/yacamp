from typing import List, Tuple, Optional
from langchain.schema import Document
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import EmbeddingsFilter

from src.ragService.config.settings import RetrieverConfig
from src.ragService.vector_store.embeddings import get_embeddings
from src.ragService.vector_store.faiss_manager import load_vector_store


def get_retriever():
    vectorstore = load_vector_store()
    if not vectorstore:
        return None

    base_retriever = vectorstore.as_retriever(
        search_kwargs={"k": RetrieverConfig.SEARCH_K * 2}
    )

    embeddings_filter = EmbeddingsFilter(
        embeddings=get_embeddings(),
        similarity_threshold=RetrieverConfig.SIMILARITY_THRESHOLD,
        k=RetrieverConfig.SEARCH_K
    )

    return ContextualCompressionRetriever(
        base_compressor=embeddings_filter,
        base_retriever=base_retriever
    )


def semantic_search(query: str) -> Tuple[List[Document], Optional[str]]:
    retriever = get_retriever()
    if not retriever:
        return [], "Ошибка инициализации поискового движка"

    try:
        retrieved_docs = retriever.invoke(query)

        # Дополнительная фильтрация результатов
        filtered_docs = []
        for doc in retrieved_docs:
            if (len(doc.page_content) > 30 and
                    hasattr(doc, 'metadata') and
                    isinstance(doc.metadata, dict)):
                filtered_docs.append(doc)

        return filtered_docs, None if filtered_docs else "Не найдено релевантных результатов"

    except Exception as e:
        return [], f"Ошибка поиска: {str(e)}"