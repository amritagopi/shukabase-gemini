#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 ПРОСТОЙ ПОИСКОВЫЙ СКРИПТ через RAGEngine

Консольный клиент для быстрого тестирования RAGEngine.

ЗАПУСК:
    python rag/quick_search.py "ваш запрос" [язык]
"""

import json
import sys
import logging
from rag.rag_engine import RAGEngine

# Отключаем излишне подробные логи для чистого вывода JSON
logging.basicConfig(level=logging.CRITICAL)

def main():
    """Основная функция для поиска через RAGEngine."""
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Query argument is missing"}), file=sys.stderr)
        print("\nUsage: python quick_search.py \"query\" [language]", file=sys.stderr)
        print("Example: python quick_search.py \"what is karma\" en", file=sys.stderr)
        sys.exit(1)

    query = sys.argv[1]
    language = sys.argv[2] if len(sys.argv) > 2 else 'ru'

    try:
        # Инициализируем движок
        engine = RAGEngine(languages=[language])
        
        # Выполняем поиск
        results = engine.search(query=query, language=language, top_k=5)
        
        # Выводим результат в формате JSON
        print(json.dumps(results, ensure_ascii=False, indent=2))

    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
