import os
from data_loader.s3_loader import download_from_s3
from data_loader.document_processor import load_documents, split_documents, validate_documents
from vector_store.faiss_manager import create_vector_store
from retriever.result_processor import get_rag_context
from config.settings import validate_config


def initialize_vector_store():
    print("Инициализация векторного хранилища...")

    # Загрузка файлов из S3
    successful_downloads, failed_downloads = download_from_s3()

    if failed_downloads:
        print(f"Не удалось загрузить файлы: {failed_downloads}")

    if not successful_downloads:
        print("Нет файлов для обработки")
        return False

    # Обработка документов
    raw_documents = load_documents(successful_downloads)
    chunks = split_documents(raw_documents)
    valid_documents = validate_documents(chunks)

    # Создание векторного хранилища
    success = create_vector_store(valid_documents)
    if success:
        print(f"Векторное хранилище создано успешно. Обработано {len(valid_documents)} чанков.")
    else:
        print("Ошибка при создании векторного хранилища")

    return success


def main():
    # Проверка конфигурации
    try:
        validate_config()
    except ValueError as e:
        print(f"Ошибка конфигурации: {e}")
        return

    # Проверка и инициализация векторного хранилища
    from vector_store.faiss_manager import load_vector_store
    if not load_vector_store():
        print("Векторное хранилище не найдено. Запуск инициализации...")
        if not initialize_vector_store():
            return

    # Пример
    while True:
        query = input("\nВведите ваш запрос (или 'quit' для выхода): ")
        if query.lower() == 'quit':
            break

        context = get_rag_context(query)
        print(f"\nКонтекст для запроса:\n{context}")


if __name__ == "__main__":
    main()