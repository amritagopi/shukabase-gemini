#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔎 ИНТЕРАКТИВНЫЙ ПОИСКОВЫЙ КЛИЕНТ ДЛЯ RAG ENGINE

Этот модуль предоставляет консольный интерфейс для тестирования RAGEngine.

ЗАПУСК:
    python rag/rag_search_service.py
"""
import logging
from rag.rag_engine import RAGEngine

# Настройка логирования, чтобы видеть сообщения от RAGEngine
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class InteractiveSearchClient:
    """Консольный клиент для RAGEngine."""
    
    def __init__(self):
        """Инициализирует клиент и RAGEngine."""
        logger.info("🏁 Запуск интерактивного поискового клиента...")
        try:
            self.engine = RAGEngine(languages=['ru', 'en'])
        except Exception as e:
            logger.critical(f"❌ Не удалось запустить RAGEngine: {e}", exc_info=True)
            self.engine = None

    def _print_results(self, results: dict):
        """Форматирует и печатает результаты поиска."""
        if not results.get('success'):
            logger.error(f"Ошибка поиска: {results.get('error')}")
            return
            
        if not results.get('results'):
            print("\n  ❌ Результатов не найдено.")
            return

        print(f"\n  🔍 Результаты для запроса: '{results.get('query', '')}'")
        if len(results.get('query_variants', [])) > 1:
            print(f"     (использовались варианты: {results['query_variants']})")

        print("-" * 70)
        for i, res in enumerate(results['results'], 1):
            score = res.get('final_score', res.get('score', 0)) * 100
            bar = '█' * int(score / 5)
            
            print(f"  {i}. [{bar:<20}] {score:.1f}%")
            print(f"     📚 Книга: {res.get('book', 'N/A')}, Глава: {res.get('chapter', 'N/A')}")
            # Ограничиваем вывод текста для читаемости
            text_preview = res.get('text', '')
            if len(text_preview) > 250:
                text_preview = text_preview[:250] + "..."
            print(f"     💬 «{text_preview}»\n")

    def run(self):
        """Запускает основной цикл интерактивного поиска."""
        if not self.engine:
            logger.error("Клиент не может быть запущен, так как RAGEngine не был инициализирован.")
            return

        print("\n" + "="*70)
        print("🔎 ИНТЕРАКТИВНЫЙ ПОИСК С RAG ENGINE")
        print("="*70)
        print("Введите запрос. Для выхода введите 'quit'.")

        while True:
            try:
                query = input("\n🔍 Запрос: ").strip()
                if not query: continue
                if query.lower() == 'quit':
                    print("👋 До встречи!")
                    break
                
                # Простой выбор языка
                lang = 'ru' if any(c in 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя' for c in query.lower()) else 'en'
                print(f"(Автоматически выбран язык: {lang.upper()})")

                results = self.engine.search(query=query, language=lang, top_k=5)
                self._print_results(results)

            except KeyboardInterrupt:
                print("\n\nПрограмма прервана.")
                break
            except Exception as e:
                logger.error(f"❌ Произошла ошибка в цикле поиска: {e}", exc_info=True)


if __name__ == "__main__":
    client = InteractiveSearchClient()
    client.run()
