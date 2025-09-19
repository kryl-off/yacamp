import os
from typing import List
from langchain.schema import Document
from langchain.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from src.ragService.config.settings import VectorStoreConfig


def load_documents(file_paths: List[str]) -> List[Document]:
    if not file_paths:
        return [Document(page_content="Нет доступных документов", metadata={})]

    all_docs = []

    for file_path in file_paths:
        try:
            if file_path.endswith(".pdf"):
                loader = PyPDFLoader(file_path)
            elif file_path.endswith(".txt"):
                loader = TextLoader(file_path, encoding="utf-8")
            else:
                continue  # Пропускаем неподдерживаемые форматы

            docs = loader.load()
            all_docs.extend(docs)
        except Exception as e:
            print(f"Ошибка загрузки файла {file_path}: {e}")
            continue

    return all_docs


def split_documents(documents: List[Document]) -> List[Document]:
    if not documents:
        return []

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=VectorStoreConfig.CHUNK_SIZE,
        chunk_overlap=VectorStoreConfig.CHUNK_OVERLAP,
        separators=["\n\n", "\n", " ", ""]
    )

    return text_splitter.split_documents(documents)


def validate_documents(documents: List[Document]) -> List[Document]:
    valid_docs = []

    for doc in documents:
        if (hasattr(doc, 'page_content') and
                isinstance(doc.page_content, str) and
                doc.page_content.strip() and
                len(doc.page_content) > 50):
            valid_docs.append(doc)

    return valid_docs if valid_docs else [
        Document(page_content="Нет корректных документов для обработки", metadata={})
    ]