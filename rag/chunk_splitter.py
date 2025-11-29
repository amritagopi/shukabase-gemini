#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
✂️  РАЗБИЕНИЕ ТЕКСТА НА ЧАНКИ ДЛЯ RAG

Этот модуль разбивает большие текстовые фрагменты на чанки оптимального размера
с перекрытием для лучшего контекста.

ЗАПУСК:
    python rag/chunk_splitter.py
"""

import json
from pathlib import Path
from typing import List, Dict
import time


class ChunkSplitter:
    """Разбивает текст на чанки с перекрытием"""
    
    def __init__(self, chunk_size=2048, overlap=256):
        """
        Args:
            chunk_size: размер чанка в символах (увеличен с 512 для скорости)
            overlap: перекрытие между чанками в символах (увеличено с 64)
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def split_text(self, text: str) -> List[str]:
        """
        Разбивает текст на чанки с защитой от зацикливания
        
        Args:
            text: исходный текст
            
        Returns:
            список чанков
        """
        if len(text) <= self.chunk_size:
            return [text] if text.strip() else []
        
        chunks = []
        start = 0
        iterations = 0
        max_iterations = (len(text) // max(self.chunk_size - self.overlap, 1)) + 100
        
        while start < len(text):
            iterations += 1
            
            # ЗАЩИТА: если слишком много итераций, значит зацикливание
            if iterations > max_iterations:
                remaining = text[start:].strip()
                if remaining:
                    chunks.append(remaining)
                break
            
            # Выбираем конечную позицию чанка
            end = min(start + self.chunk_size, len(text))
            
            # Если не конец текста, ищем хорошую точку разделения
            if end < len(text):
                search_start = max(start, end - 100)
                search_area = text[search_start:end]
                
                # Ищем последнюю точку/восклицание/вопрос (БЕЗ regex для скорости)
                for i in range(len(search_area) - 1, -1, -1):
                    if search_area[i] in '.!?':
                        end = search_start + i + 1
                        break
                else:
                    # Если нет точки, ищем пробел
                    last_space = text.rfind(' ', start, end)
                    if last_space > start:
                        end = last_space
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # КЛЮЧЕВОЕ ИСПРАВЛЕНИЕ: убедиться, что мы двигаемся вперед
            step = self.chunk_size - self.overlap
            if step <= 0:
                step = max(1, self.chunk_size // 2)
            
            old_start = start
            start = end - self.overlap
            
            # Если прогресс слишком мал, делаем больший прыжок
            if start <= old_start + step // 10:
                start = end
        
        return chunks
    
    def chunk_parsed_scripture(self, parsed_data: Dict, language: str = 'ru'):
        """
        Разбивает распарсенные писания на чанки
        
        Args:
            parsed_data: словарь распарсенных писаний
            language: язык ('ru' или 'en')
            
        Returns:
            словарь с чанками
        """
        chunked_data = {}
        total_chunks = 0
        
        for book_name in sorted(parsed_data.keys()):
            print(f"  📖 Обработка {book_name}...")
            
            chunked_data[book_name] = {}
            book_chunks = 0
            file_count = 0
            
            for file_path, text in parsed_data[book_name].items():
                file_count += 1
                chunks = self.split_text(text)
                
                if chunks:
                    chunked_data[book_name][file_path] = chunks
                    book_chunks += len(chunks)
                    total_chunks += len(chunks)
                
                # Логируем прогресс каждые 100 файлов
                if file_count % 100 == 0:
                    print(f"    ⏳ Обработано {file_count} файлов... ({total_chunks} чанков)")
            
            print(f"    ✅ Создано {book_chunks} чанков из {file_count} файлов")
        
        return chunked_data, total_chunks
    
    def process_language(self, language: str = 'ru') -> tuple:
        """
        Полный процесс обработки одного языка
        
        Args:
            language: 'ru' или 'en'
            
        Returns:
            (chunked_data, stats_dict)
        """
        parsed_file = f"rag/parsed_scriptures_{language}.json"
        output_file = f"rag/chunked_scriptures_{language}.json"
        
        if not Path(parsed_file).exists():
            print(f"⚠️  Файл {parsed_file} не найден. Пропускаю обработку {language}.")
            return None, None
        if Path(output_file).exists():
            print(f"⏩ {output_file} уже существует. Пропускаю обработку {language}.")
            file_size = Path(output_file).stat().st_size / (1024*1024)
            stats = {
                'language': language,
                'total_books': None,
                'total_chunks': None,
                'chunk_size': self.chunk_size,
                'overlap': self.overlap,
                'output_file': output_file,
                'file_size_mb': file_size,
                'elapsed_seconds': 0
            }
            return None, stats
        print(f"\n🔍 Загружаю {parsed_file}...")
        start_time = time.time()
        with open(parsed_file, 'r', encoding='utf-8') as f:
            parsed_data = json.load(f)
        print(f"✅ Загружено {len(parsed_data)} книг")
        print(f"\n✂️  Разбиваю текст на чанки (chunk_size={self.chunk_size}, overlap={self.overlap})...")
        chunked_data, total_chunks = self.chunk_parsed_scripture(parsed_data, language)
        print(f"\n💾 Сохраняю в {output_file}...")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(chunked_data, f, ensure_ascii=False, indent=2)
        file_size = Path(output_file).stat().st_size / (1024*1024)
        elapsed = time.time() - start_time
        print(f"✅ Файл сохранён! Размер: {file_size:.2f} МБ")
        print(f"⏱️  Время обработки: {elapsed:.1f} сек ({elapsed/60:.1f} мин)")
        # Собираем статистику
        stats = {
            'language': language,
            'total_books': len(chunked_data),
            'total_chunks': total_chunks,
            'chunk_size': self.chunk_size,
            'overlap': self.overlap,
            'output_file': output_file,
            'file_size_mb': file_size,
            'elapsed_seconds': elapsed
        }
        return chunked_data, stats


def process_all_languages():
    """Обрабатывает оба языка"""
    
    print("="*70)
    print("✂️  РАЗБИЕНИЕ ТЕКСТА НА ЧАНКИ")
    print("="*70)
    
    import sys
    splitter = ChunkSplitter(chunk_size=2048, overlap=256)
    all_stats = {}
    langs = []
    # CLI: python chunk_splitter.py [ru|en|all]
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ('ru', 'en'):
            langs = [arg]
        else:
            langs = ['ru', 'en']
    else:
        langs = ['ru', 'en']
    for lang in langs:
        print(f"\n📍 ЭТАП: {lang.upper()} ПИСАНИЯ")
        print("-" * 70)
        _, stats = splitter.process_language(lang)
        all_stats[lang] = stats
    print("\n" + "="*70)
    print("✅ РАЗБИЕНИЕ ЗАВЕРШЕНО!")
    print("="*70)
    total_time = sum(stats['elapsed_seconds'] for stats in all_stats.values() if stats and 'elapsed_seconds' in stats)
    for lang, stats in all_stats.items():
        print(f"\n📊 {lang.upper()}:")
        if stats:
            print(f"   📚 Книг: {stats['total_books']}")
            print(f"   📄 Всего чанков: {stats['total_chunks']}")
            print(f"   💾 Размер файла: {stats['file_size_mb']:.2f} МБ")
            print(f"   ⏱️  Время: {stats['elapsed_seconds']:.1f} сек")
            print(f"   📝 Параметры: chunk_size={stats['chunk_size']}, overlap={stats['overlap']}")
        else:
            print("   ⚠️  Не обработано.")
    print(f"\n⏱️  ОБЩЕЕ ВРЕМЯ: {total_time:.1f} сек ({total_time/60:.2f} мин)")
    print("\n👉 Следующий шаг: Создание эмбеддингов для RAG")
    return all_stats


if __name__ == "__main__":
    process_all_languages()
