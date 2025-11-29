#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 ЗАПУСК ПАРСЕРА SHUKABASE

Этот скрипт запускает парсер и создаёт JSON файлы с извлечённым текстом.

ЗАПУСК:
    python rag/run_parser_locally.py

РЕЗУЛЬТАТЫ:
    - rag/parsed_scriptures_ru.json  (русские писания)
    - rag/parsed_scriptures_en.json  (английские писания, опционально)
"""

import sys
from pathlib import Path
import time

# Добавляем папку rag в path, чтобы найти parser.py
sys.path.insert(0, str(Path(__file__).parent))

from parser import parse_scriptures_for_language


def main():
    print("="*70)
    print("🚀 ЗАПУСК ПАРСЕРА SHUKABASE")
    print("="*70)
    print()
    
    # Проверяем наличие папки cleaned_vedabase
    if not Path("cleaned_vedabase").exists():
        print("❌ ОШИБКА: Папка 'cleaned_vedabase' не найдена!")
        print("❌ Убедитесь, что вы запускаете скрипт из корневой папки SHUKABASE")
        return False
    
    # Проверяем наличие BeautifulSoup
    try:
        import bs4
    except ImportError:
        print("❌ ОШИБКА: BeautifulSoup4 не установлен!")
        print("   Установите его командой:")
        print("   pip install beautifulsoup4")
        return False
    
    print("✅ Все зависимости найдены!")
    print()
    
    start_time = time.time()
    
    # Парсим русские писания
    print("📍 ЭТАП 1: Парсинг РУССКИХ писаний")
    print("-" * 70)
    parse_scriptures_for_language('ru', 'rag/parsed_scriptures_ru.json')
    
    print()
    print("📍 ЭТАП 2: Парсинг АНГЛИЙСКИХ писаний (это займёт время...)")
    print("-" * 70)
    parse_scriptures_for_language('en', 'rag/parsed_scriptures_en.json')
    
    elapsed_time = time.time() - start_time
    
    print()
    print("="*70)
    print("✅ ПАРСИНГ ЗАВЕРШЁН!")
    print("="*70)
    print(f"⏱️  Время выполнения: {elapsed_time:.1f} сек ({elapsed_time/60:.1f} мин)")
    print()
    print("📊 Созданы файлы:")
    print("   ✅ rag/parsed_scriptures_ru.json")
    print("   ✅ rag/parsed_scriptures_en.json")
    print()
    print("👉 Следующий шаг: Разбиение текста на чанки для RAG")
    print()
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
