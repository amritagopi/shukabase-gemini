#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠 ГЕНЕРАЦИЯ ЭМБЕДДИНГОВ ДЛЯ RAG

Этот модуль создает векторные представления (эмбеддинги) чанков текста
для использования в системе поиска по семантическому сходству.
Он использует Google Gemini API.

ЗАПУСК:
    python rag/embeddings_generator.py
"""

import json
import numpy as np
from pathlib import Path
from typing import Dict, List
import time
import os
import google.generativeai as genai
from dotenv import load_dotenv

class EmbeddingsGenerator:
    """Генерирует эмбеддинги для чанков текста с помощью Google Gemini API"""
    
    def __init__(self):
        """
        Инициализирует генератор, используя модель text-embedding-004.
        """
        self.model_name = "models/text-embedding-004"
        self.embedding_dim = 768  # Размерность для text-embedding-004
        print(f"🔄 Инициализирован генератор с моделью: {self.model_name}")
        print(f"📏 Размерность эмбеддинга: {self.embedding_dim}")
    
    def generate_embeddings(self, chunks_data: Dict[str, Dict[str, List[str]]], 
                          language: str = 'ru', batch_size: int = 100) -> Dict:
        """
        Генерирует эмбеддинги для всех чанков через Google Gemini API
        
        Args:
            chunks_data: словарь с чанками
            language: язык ('ru' или 'en')
            batch_size: размер батча для обработки (max 100 для Gemini API)
            
        Returns:
            словарь с эмбеддингами и метаданными
        """
        if batch_size > 100:
            print(f"⚠️ Размер батча ({batch_size}) превышает лимит API (100). Устанавливаю 100.")
            batch_size = 100

        embeddings_data = {
            'model': self.model_name,
            'embedding_dim': self.embedding_dim,
            'language': language,
            'books': {}
        }
        
        total_chunks = 0
        total_embeddings = 0
        
        # Собираем все чанки для обработки
        all_chunks_with_info = []
        
        for book_name in sorted(chunks_data.keys()):
            embeddings_data['books'][book_name] = {}
            
            for file_path in sorted(chunks_data[book_name].keys()):
                embeddings_data['books'][book_name][file_path] = []
                
                for chunk_idx, chunk_text in enumerate(chunks_data[book_name][file_path]):
                    all_chunks_with_info.append({
                        'text': chunk_text,
                        'book': book_name,
                        'file': file_path,
                        'chunk_idx': chunk_idx
                    })
                    total_chunks += 1
        
        print(f"📊 Всего чанков для обработки: {total_chunks:,}")
        print(f"🔄 Генерирую эмбеддинги (batch_size={batch_size}). Это может занять время...\n")
        
        # Генерируем эмбеддинги батчами
        start_time = time.time()
        
        for batch_start in range(0, len(all_chunks_with_info), batch_size):
            batch_end = min(batch_start + batch_size, len(all_chunks_with_info))
            batch_info = all_chunks_with_info[batch_start:batch_end]
            
            texts = [item['text'] for item in batch_info]
            
            try:
                # Генерируем эмбеддинги через API
                result = genai.embed_content(
                    model=self.model_name,
                    content=texts,
                    task_type="RETRIEVAL_DOCUMENT" # Оптимизация для поиска документов
                )
                batch_embeddings = result['embedding']
                
                # Сохраняем эмбеддинги в структуру данных
                for i, item in enumerate(batch_info):
                    embedding = batch_embeddings[i]
                    embeddings_data['books'][item['book']][item['file']].append({
                        'chunk_idx': item['chunk_idx'],
                        'text_preview': item['text'][:100],
                        'embedding': embedding
                    })
                    total_embeddings += 1

                # Логируем прогресс
                progress_pct = (batch_end / len(all_chunks_with_info)) * 100
                elapsed = time.time() - start_time
                rate = total_embeddings / elapsed if elapsed > 0 else 0
                eta = (len(all_chunks_with_info) - total_embeddings) / rate if rate > 0 else 0
                
                print(f"  ⏳ {progress_pct:5.1f}% | {total_embeddings:7,} эмбеддингов | {rate:5.1f} шт/сек | ETA: {eta:6.0f}сек")

                # Пауза, чтобы не превышать лимиты API (например, 60 запросов в минуту)
                time.sleep(1)

            except Exception as e:
                print(f"\n❌ Ошибка при обработке батча {batch_start}-{batch_end}: {e}")
                print("   Пропускаю этот батч. Проверьте соединение и API ключ.")
                continue

        elapsed = time.time() - start_time
        print(f"\n✅ Эмбеддинги созданы за {elapsed:.1f} сек ({elapsed/60:.1f} мин)")
        
        return embeddings_data
    
    def save_embeddings(self, embeddings_data: Dict, language: str = 'ru'):
        """
        Сохраняет эмбеддинги в файл (в сжатом виде с NumPy)
        """
        # ... (этот метод остается без изменений)
        output_file = f"rag/embeddings_{language}.npz"
        
        print(f"\n💾 Сохраняю эмбеддинги в {output_file}...")
        
        embeddings_arrays = {}
        metadata = {
            'model': embeddings_data['model'],
            'embedding_dim': embeddings_data['embedding_dim'],
            'language': embeddings_data['language'],
            'structure': {}
        }
        
        idx = 0
        for book_name in sorted(embeddings_data['books'].keys()):
            metadata['structure'][book_name] = {}
            
            for file_path in sorted(embeddings_data['books'][book_name].keys()):
                chunk_list = embeddings_data['books'][book_name][file_path]
                
                if chunk_list:
                    embeddings_matrix = np.array([item['embedding'] for item in chunk_list])
                    key = f"embeddings_{idx}"
                    embeddings_arrays[key] = embeddings_matrix
                    
                    metadata['structure'][book_name][file_path] = {
                        'embedding_key': key,
                        'num_chunks': len(chunk_list),
                        'text_previews': [item['text_preview'] for item in chunk_list]
                    }
                    idx += 1
        
        np.savez_compressed(output_file, **embeddings_arrays)
        
        metadata_file = f"rag/embeddings_metadata_{language}.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        npz_size = Path(output_file).stat().st_size / (1024*1024)
        json_size = Path(metadata_file).stat().st_size / (1024*1024)
        
        print(f"✅ NPZ файл сохранён: {npz_size:.2f} МБ")
        print(f"✅ Метаданные сохранены: {json_size:.2f} МБ")
        
        return output_file, metadata_file

    def process_language(self, language: str = 'ru'):
        """
        Полный процесс для одного языка
        """
        chunked_file = f"rag/chunked_scriptures_{language}.json"
        
        print(f"\n🔍 Загружаю чанки из {chunked_file}...")
        with open(chunked_file, 'r', encoding='utf-8') as f:
            chunks_data = json.load(f)
        
        print(f"✅ Загружено {len(chunks_data)} книг")
        
        embeddings_data = self.generate_embeddings(chunks_data, language=language, batch_size=100)
        
        if sum(len(file_data) for book_data in embeddings_data['books'].values() for file_data in book_data.values()) == 0:
            print("❌ Не было сгенерировано ни одного эмбеддинга. Процесс прерван.")
            return None

        npz_file, json_file = self.save_embeddings(embeddings_data, language=language)
        
        stats = {
            'language': language,
            'total_books': len(embeddings_data['books']),
            'embedding_model': embeddings_data['model'],
            'embedding_dim': embeddings_data['embedding_dim'],
            'npz_file': npz_file,
            'metadata_file': json_file
        }
        
        return stats


def process_all_languages():
    """Обрабатывает эмбеддинги для обоих языков"""
    
    print("="*70)
    print("🧠 ГЕНЕРАЦИЯ ЭМБЕДДИНГОВ ДЛЯ RAG (GOOGLE GEMINI API)")
    print("="*70)

    # Загружаем API ключ из .env файла
    load_dotenv()
    if 'GEMINI_API_KEY' not in os.environ:
        print("❌ ОШИБКА: Переменная окружения GEMINI_API_KEY не найдена.")
        print("   Пожалуйста, создайте файл .env в корне проекта и добавьте в него строку:")
        print("   GEMINI_API_KEY='Ваш_ключ'")
        return
    
    try:
        genai.configure(api_key=os.environ['GEMINI_API_KEY'])
        print("✅ Ключ Gemini API успешно сконфигурирован.")
    except Exception as e:
        print(f"❌ Ошибка при конфигурации Gemini API: {e}")
        return

    generator = EmbeddingsGenerator()
    
    all_stats = {}
    
    # Русские писания
    print("\n📍 ЭТАП 1: ЭМБЕДДИНГИ ДЛЯ РУССКИХ ПИСАНИЙ")
    print("-" * 70)
    stats_ru = generator.process_language('ru')
    if stats_ru:
        all_stats['ru'] = stats_ru
    
    # Английские писания
    print("\n📍 ЭТАП 2: ЭМБЕДДИНГИ ДЛЯ АНГЛИЙСКИХ ПИСАНИЙ")
    print("-" * 70)
    stats_en = generator.process_language('en')
    if stats_en:
        all_stats['en'] = stats_en
    
    print("\n" + "="*70)
    if not all_stats:
        print("❌ ГЕНЕРАЦИЯ ЭМБЕДДИНГОВ ЗАВЕРШИЛАСЬ С ОШИБКАМИ.")
    else:
        print("✅ ГЕНЕРАЦИЯ ЭМБЕДДИНГОВ ЗАВЕРШЕНА!")
    print("="*70)
    
    for lang, stats in all_stats.items():
        print(f"\n📊 {lang.upper()}:")
        print(f"   📚 Книг: {stats['total_books']}")
        print(f"   🧠 Модель: {stats['embedding_model']}")
        print(f"   📏 Размерность: {stats['embedding_dim']}")
        print(f"   💾 NPZ файл: {stats['npz_file']}")
        print(f"   📝 Метаданные: {stats['metadata_file']}")
    
    if all_stats:
        print("\n👉 Следующий шаг: Создание индекса для быстрого поиска (FAISS)")
    
    return all_stats


if __name__ == "__main__":
    process_all_languages()
