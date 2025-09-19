from typing import List
from langchain.schema import Document


def format_context(documents: List[Document]) -> str:
    if not documents:
        return "Нет релевантной информации в документах."

    context_parts = []
    for i, doc in enumerate(documents, 1):
        content = doc.page_content.strip()
        source = doc.metadata.get('source', 'Неизвестный источник')
        context_parts.append(f"[Документ {i} из {source}]:\n{content}")

    return "\n\n".join(context_parts)


def get_rag_context(query: str) -> str:
    from src.ragService.retriever.semantic_retriever import semantic_search

    documents, error = semantic_search(query)
    if error:
        return f"Контекст недоступен. Причина: {error}"

    return format_context(documents)