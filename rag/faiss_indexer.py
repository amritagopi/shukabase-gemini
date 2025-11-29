#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 СОЗДАНИЕ ИНДЕКСА FAISS ДЛЯ БЫСТРОГО ПОИСКА

Этот модуль создает индекс FAISS для быстрого семантического поиска
по эмбеддингам чанков.

ЗАПУСК:
    python rag/faiss_indexer.py
"""

import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Any
import time

try:
    import faiss
except ImportError:
    print("⚠️  FAISS не установлен. Установите с помощью:")
    print("   pip install faiss-cpu  (или faiss-gpu для GPU)")
    exit(1)


class FAISSIndexer:
    def __init__(self, embedding_dim: int = 768): # Обновленная размерность для text-embedding-004
        """
        Args:
            embedding_dim: размерность эмбеддингов
        """
        self.embedding_dim = embedding_dim
        # Создаем индекс с использованием IVFFlat для больших наборов данных
        # Количество кластеров (nlist) должно быть подобрано для вашего датасета
        self.quantizer = faiss.IndexFlatL2(embedding_dim)
        self.index = faiss.IndexIVFFlat(self.quantizer, embedding_dim, 100) # 100 - разумное число кластеров
        self.index.nprobe = 10 # Количество ближайших кластеров для поиска
    
    def load_embeddings(self, language: str = 'ru') -> Tuple[np.ndarray, Dict]:
        """
        Загружает сохраненные эмбеддинги из .npz файла
        
        Args:
            language: 'ru' или 'en'
            
        Returns:
            (embeddings_matrix, metadata)
        """
        metadata_file = f"rag/embeddings_metadata_{language}.json"
        npz_file = f"rag/embeddings_{language}.npz" # Изменено на .npz
        
        print(f"📂 Загружаю эмбеддинги из {npz_file}...")
        if not Path(npz_file).exists():
            print(f"⚠️  Файл {npz_file} не найден. Пропускаю обработку {language}.")
            return None, None
        
        # Загрузка NPZ файла и извлечение эмбеддингов
        npz_data = np.load(npz_file)
        # Объединяем все массивы из npz в один
        embeddings_list = [npz_data[key] for key in sorted(npz_data.files) if key.startswith('embeddings_')]
        
        if not embeddings_list:
            print(f"❌ В файле {npz_file} не найдено массивов эмбеддингов. Пропускаю обработку {language}.")
            return None, None
            
        embeddings = np.vstack(embeddings_list).astype('float32')
        
        print(f"✅ Загружено {embeddings.shape[0]:,} эмбеддингов размерности {embeddings.shape[1]}")
        
        if not Path(metadata_file).exists():
            print(f"⚠️  Файл {metadata_file} не найден. Пропускаю обработку {language}.")
            return None, None
            
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
            
        return embeddings, metadata
        
    def build_index(self, embeddings: np.ndarray) -> faiss.Index:
        """
        Строит FAISS индекс из массива эмбеддингов.
        
        Args:
            embeddings: массив эмбеддингов
            
        Returns:
            Построенный FAISS индекс
        """
        print(f"\n🔨 Строю FAISS индекс для {embeddings.shape[0]:,} эмбеддингов...")
        start_time = time.time()
        
        # Нормализуем эмбеддинги перед добавлением в индекс
        faiss.normalize_L2(embeddings)
        
        # Выбираем тип индекса в зависимости от количества эмбеддингов
        # IndexFlatL2 - простой, для небольших наборов данных
        # IndexIVFFlat - более сложный, для больших наборов данных, требует обучения
        if embeddings.shape[0] < 10000: # Можно настроить порог
            index = faiss.IndexFlatL2(self.embedding_dim)
            print(f"  📍 Используется IndexFlatL2")
            index.add(embeddings)
        else:
            # Инициализация IndexIVFFlat требует обучения
            quantizer = faiss.IndexFlatL2(self.embedding_dim)
            nlist = min(100, int(np.sqrt(embeddings.shape[0]))) # Количество кластеров, эвристика
            index = faiss.IndexIVFFlat(quantizer, self.embedding_dim, nlist, faiss.METRIC_L2)
            index.nprobe = min(50, nlist) # Количество кластеров для поиска
            print(f"  📍 Используется IndexIVFFlat с {nlist} кластерами, nprobe={index.nprobe}")
            
            # Обучение индекса
            if not index.is_trained:
                print("  ⚙️ Обучаю IndexIVFFlat (может занять некоторое время)...")
                index.train(embeddings)
                print("  ✅ Обучение завершено.")
            
            index.add(embeddings)
        
        elapsed = time.time() - start_time
        print(f"✅ Индекс построен за {elapsed:.1f} сек")
        return index
    
    def save_index(self, index: faiss.Index, metadata: Dict, language: str = 'ru'):
        """
        Сохраняет FAISS индекс и метаданные в файлы.
        """
        index_file = f"rag/faiss_index_{language}.bin"
        metadata_file = f"rag/faiss_metadata_{language}.json"
        
        print(f"\n💾 Сохраняю индекс в {index_file}...")
        faiss.write_index(index, index_file)
        index_size = Path(index_file).stat().st_size / (1024*1024)
        print(f"✅ Индекс сохранён: {index_size:.2f} МБ")
        
        # Добавляем информацию о модели эмбеддингов в метаданные индекса
        metadata['embedding_model'] = "models/text-embedding-004"
        metadata['embedding_dim'] = self.embedding_dim

        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        metadata_size = Path(metadata_file).stat().st_size / (1024*1024)
        print(f"✅ Метаданные сохранены: {metadata_size:.2f} МБ")
        return index_file, metadata_file

    def process_language(self, language: str = 'ru') -> Dict[str, Any]:
        """
        Полный процесс создания индекса для одного языка.
        """
        index_file = f"rag/faiss_index_{language}.bin"
        metadata_file_out = f"rag/faiss_metadata_{language}.json"

        # Проверяем, существует ли индекс и метаданные
        if Path(index_file).exists() and Path(metadata_file_out).exists():
            index_size = Path(index_file).stat().st_size / (1024*1024)
            print(f"⏩ Индекс и метаданные для {language} уже существуют ({index_size:.2f} МБ). Пропускаю обработку.")
            
            # Загружаем существующие метаданные, чтобы вернуть их в статистику
            with open(metadata_file_out, 'r', encoding='utf-8') as f:
                existing_metadata = json.load(f)
            
            return {
                'language': language,
                'total_embeddings': existing_metadata.get('total_embeddings', 'N/A'),
                'embedding_dim': existing_metadata.get('embedding_dim', self.embedding_dim),
                'index_file': index_file,
                'metadata_file': metadata_file_out
            }

        embeddings, metadata = self.load_embeddings(language)
        
        if embeddings is None or metadata is None:
            return None

        index = self.build_index(embeddings)
        index_file, metadata_file = self.save_index(index, metadata, language)
        
        # Тестирование поиска (опционально, можно добавить сюда)
        # self.test_search(index, embeddings, metadata, language)
        
        stats = {
            'language': language,
            'total_embeddings': embeddings.shape[0],
            'embedding_dim': embeddings.shape[1],
            'index_file': index_file,
            'metadata_file': metadata_file
        }
        return stats


def process_all_languages():
    """Обрабатывает индексы для обоих языков."""
    
    print("="*70)
    print("🔍 СОЗДАНИЕ FAISS ИНДЕКСОВ")
    print("="*70)
    
    indexer = FAISSIndexer(embedding_dim=768) # Обновленная размерность
    
    all_stats = {}
    
    print("\n📍 ЭТАП 1: ИНДЕКС ДЛЯ РУССКИХ ПИСАНИЙ")
    print("-" * 70)
    stats_ru = indexer.process_language('ru')
    if stats_ru:
        all_stats['ru'] = stats_ru
    
    print("\n📍 ЭТАП 2: ИНДЕКС ДЛЯ АНГЛИЙСКИХ ПИСАНИЙ")
    print("-" * 70)
    stats_en = indexer.process_language('en')
    if stats_en:
        all_stats['en'] = stats_en
    
    print("\n" + "="*70)
    if not all_stats:
        print("❌ ИНДЕКСИРОВАНИЕ ЗАВЕРШИЛОСЬ С ОШИБКАМИ ИЛИ БЕЗ СОЗДАНИЯ ИНДЕКСОВ.")
    else:
        print("✅ ИНДЕКСИРОВАНИЕ ЗАВЕРШЕНО!")
    print("="*70)
    
    for lang, stats in all_stats.items():
        print(f"\n📊 {lang.upper()}:")
        if stats:
            print(f"   🔢 Всего эмбеддингов: {stats['total_embeddings']:,}")
            print(f"   📏 Размерность: {stats['embedding_dim']}")
            print(f"   📚 Индекс: {stats['index_file']}")
            print(f"   📝 Метаданные: {stats['metadata_file']}")
        else:
            print("   ⚠️ Пропуск (вероятно, отсутствовали эмбеддинги).")
    
    if all_stats:
        print("\n✨ RAG система готова к использованию!")
        print("👉 Теперь вы можете запустить API сервер: python rag/rag_api_server.py")
    
    return all_stats


if __name__ == "__main__":
    process_all_languages()
