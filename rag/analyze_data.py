#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📊 АНАЛИЗАТОР ДАННЫХ SHUKABASE

Этот скрипт анализирует структуру HTML-файлов в папке cleaned_vedabase
и выводит подробную статистику.

ЗАПУСК:
    python rag/analyze_data.py
"""

import os
from pathlib import Path
from collections import defaultdict

def analyze_html_files():
    """
    Анализирует структуру HTML файлов в cleaned_vedabase
    """
    print("="*70)
    print("📚 АНАЛИЗ ДАННЫХ SHUKABASE")
    print("="*70)
    print()
    
    # Проверяем наличие папки
    data_dir = Path("cleaned_vedabase")
    
    if not data_dir.exists():
        print("❌ ОШИБКА: Папка 'cleaned_vedabase' не найдена!")
        print("‼️  Убедитесь, что вы запускаете скрипт из корневой папки SHUKABASE")
        return
    
    # Анализируем русские книги
    ru_dir = data_dir / "ru"
    en_dir = data_dir / "en"
    
    for lang, lang_name in [(ru_dir, "Русские"), (en_dir, "Английские")]:
        if not lang.exists():
            print(f"⚠️  Папка {lang} не найдена, пропускаем...")
            continue
            
        print(f"📚 {lang_name} писания:")
        print("-" * 70)
        
        # Собираем статистику по книгам
        books = defaultdict(int)
        html_files = list(lang.rglob("*.html"))
        
        for html_file in html_files:
            try:
                parts = html_file.relative_to(lang).parts
                if len(parts) > 0:
                    book_code = parts[0]
                    books[book_code] += 1
            except Exception as e:
                print(f"⚠️  Ошибка при обработке {html_file}: {e}")
        
        if not books:
            print("  🚫 Файлы не найдены")
        else:
            # Сортируем книги по коду
            for book_code in sorted(books.keys()):
                count = books[book_code]
                print(f"  📖 {book_code:15s} - {count:5d} файлов")
        
        # Итоговая статистика
        total_files = len(html_files)
        print()
        print(f"  📊 Всего книг: {len(books)}")
        print(f"  📄 Всего HTML файлов: {total_files:,}")
        
        # Подсчитываем примерный размер
        total_size = 0
        for html_file in html_files:
            try:
                total_size += html_file.stat().st_size
            except:
                pass
        
        size_mb = total_size / (1024 * 1024)
        print(f"  💾 Общий размер: {size_mb:.2f} МБ")
        print()
    
    print("="*70)
    print("✅ Анализ завершён!")
    print("="*70)
    print()
    print("👉 Следующий шаг: запустите парсер для извлечения текста")
    print("   python rag/run_parser_locally.py")
    print()

if __name__ == "__main__":
    try:
        analyze_html_files()
    except Exception as e:
        print(f"❌ Произошла ошибка: {e}")
        import traceback
        traceback.print_exc()