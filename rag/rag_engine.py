"""
🧠 RAG ENGINE - Векторный поиск с Re-ranking для Shukabase

Этот модуль предоставляет:
1. Векторный поиск с использованием Google Gemini API
2. FAISS индексирование для быстрого поиска
3. Re-ranking с помощью Jina Reranker
4. Переформулировка запросов с синонимами
"""

import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Any
import logging
import os
import time

# Управление зависимостями
try:
    import faiss
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    import torch
    import google.generativeai as genai
    from dotenv import load_dotenv
except ImportError as e:
    raise ImportError(
        f"Отсутствует зависимость: {e}. "
        "Установите необходимые пакеты: pip install faiss-cpu transformers torch google-generativeai python-dotenv"
    )

logger = logging.getLogger(__name__)

# --- Вспомогательные классы (QueryExpander, RerankerModel) без изменений ---

class QueryExpander:
    """Расширение и переформулировка запросов"""
    
    SYNONYMS_RU = {
        "любовь": ["преданность", "бхакти", "дружба", "привязанность"],
        "бог": ["кришна", "верховный", "абсолют", "божество"],
        "душа": ["атма", "дух", "сознание", "сущность"],
        "знание": ["джняна", "мудрость", "понимание", "осознание"],
        "йога": ["практика", "медитация", "дисциплина", "путь"],
        "карма": ["действие", "деяние", "следствие", "судьба"],
        "освобождение": ["мокша", "спасение", "свобода", "выход"],
        "мир": ["материальный", "вселенная", "временный", "преходящий"],
    }
    
    SYNONYMS_EN = {
        "love": ["devotion", "bhakti", "affection", "attachment"],
        "god": ["krishna", "supreme", "absolute", "deity"],
        "soul": ["atma", "spirit", "consciousness", "essence"],
        "knowledge": ["jnana", "wisdom", "understanding", "realization"],
        "yoga": ["practice", "meditation", "discipline", "path"],
        "karma": ["action", "deed", "consequence", "fate"],
        "liberation": ["moksha", "salvation", "freedom", "release"],
        "world": ["material", "universe", "temporary", "transient"],
    }
    
    @staticmethod
    def expand_query_ru(query: str) -> List[str]:
        expanded = [query]
        query_lower = query.lower()
        for term, synonyms in QueryExpander.SYNONYMS_RU.items():
            if term in query_lower:
                for synonym in synonyms[:2]:
                    expanded.append(query.lower().replace(term, synonym))
        return list(set(expanded))[:3]
    
    @staticmethod
    def expand_query_en(query: str) -> List[str]:
        expanded = [query]
        query_lower = query.lower()
        for term, synonyms in QueryExpander.SYNONYMS_EN.items():
            if term in query_lower:
                for synonym in synonyms[:2]:
                    expanded.append(query.lower().replace(term, synonym))
        return list(set(expanded))[:3]


class RerankerModel:
    """Модель re-ranking для переоценки релевантности"""
    
    def __init__(self, model_name: str = "jinaai/jina-reranker-v2-base-multilingual"):
        logger.info(f"Загружаю модель re-ranking: {model_name}")
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
            self.model = AutoModelForSequenceClassification.from_pretrained(
                model_name, trust_remote_code=True, torch_dtype=torch.float32
            )
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model.to(self.device)
            self.model.eval()
            logger.info(f"✅ Модель re-ranking загружена (device: {self.device})")
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки модели re-ranking: {e}")
            self.model = None
    
    def rerank(self, query: str, documents: List[str], top_k: int = 5) -> List[Tuple[int, float, str]]:
        if not self.model or not documents:
            return [(i, 1.0, doc) for i, doc in enumerate(documents)][:top_k]
        try:
            with torch.no_grad():
                inputs = self.tokenizer(
                    [[query, doc] for doc in documents],
                    padding=True, truncation=True, return_tensors="pt", max_length=512
                ).to(self.device)
                scores = self.model(**inputs, return_dict=True).logits.squeeze(-1).cpu().numpy()
            
            ranked = sorted([(i, score, documents[i]) for i, score in enumerate(scores)], key=lambda x: x[1], reverse=True)
            return ranked[:top_k]
        except Exception as e:
            logger.error(f"Ошибка при re-ranking: {e}")
            return [(i, 1.0, doc) for i, doc in enumerate(documents)][:top_k]


# --- Обновленный RAGEngine ---

class RAGEngine:
    """Главный класс RAG системы с Google Gemini API"""
    
    def __init__(
        self,
        reranker_model: str = "jinaai/jina-reranker-v2-base-multilingual",
        languages: List[str] = ['ru', 'en'],
        base_dir: str = "rag"
    ):
        logger.info("🚀 Инициализирую RAG Engine...")
        
        self._configure_gemini_api()
        
        self.base_dir = Path(base_dir)
        self.embedding_model_name = "models/text-embedding-004"
        self.languages = languages
        
        self.reranker = RerankerModel(reranker_model)
        
        self.indices: Dict[str, faiss.Index] = {}
        self.metadata: Dict[str, Any] = {}
        self.chunked_data: Dict[str, Dict] = {}
        
        for lang in languages:
            self._load_language_data(lang)
        
        logger.info("✅ RAG Engine готов к работе!")

    def _configure_gemini_api(self):
        """Загружает и настраивает ключ API для Gemini."""
        load_dotenv()
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("Переменная окружения GEMINI_API_KEY не найдена.")
        try:
            genai.configure(api_key=api_key)
            logger.info("✅ Ключ Gemini API успешно сконфигурирован.")
        except Exception as e:
            raise RuntimeError(f"❌ Ошибка при конфигурации Gemini API: {e}")

    def _load_language_data(self, language: str):
        """Загружает индекс, метаданные и чанки для указанного языка."""
        index_file = self.base_dir / f"faiss_index_{language}.bin"
        metadata_file = self.base_dir / f"faiss_metadata_{language}.json"
        chunks_file = self.base_dir / f"chunked_scriptures_{language}.json"

        if not index_file.exists():
            logger.warning(f"⚠️ Индекс FAISS не найден: {index_file}")
            return
            
        logger.info(f"📂 Загружаю данные для языка '{language}'...")
        self.indices[language] = faiss.read_index(str(index_file))
        logger.info(f"  - Загружено {self.indices[language].ntotal:,} векторов из {index_file}")

        if metadata_file.exists():
            with open(metadata_file, 'r', encoding='utf-8') as f:
                raw_metadata = json.load(f)
            
            # Flatten metadata to match FAISS indices
            flat_metadata = []
            structure = raw_metadata.get('structure', {})
            
            # Collect all chapters
            all_chapters = []
            for book_key, book_data in structure.items():
                for chapter_key, chapter_data in book_data.items():
                    if 'embedding_key' in chapter_data:
                        all_chapters.append({
                            'book': book_key,
                            'chapter': chapter_key,
                            'data': chapter_data
                        })
            
            # Sort by embedding_key index (e.g., embeddings_0, embeddings_1)
            def get_embedding_index(item):
                key = item['data']['embedding_key']
                try:
                    return int(key.split('_')[1])
                except (IndexError, ValueError):
                    return 999999
            
            all_chapters.sort(key=get_embedding_index)
            
            # Create flat list
            for item in all_chapters:
                book = item['book']
                chapter = item['chapter']
                data = item['data']
                num_chunks = data.get('num_chunks', 0)
                text_previews = data.get('text_previews', [])
                
                for i in range(num_chunks):
                    preview = text_previews[i] if i < len(text_previews) else ""
                    flat_metadata.append({
                        'book': book,
                        'chapter': chapter,
                        'chunk_idx': i,
                        'text_preview': preview
                    })
            
            self.metadata[language] = flat_metadata
            logger.info(f"  - Загружены и обработаны метаданные ({len(flat_metadata)} записей)")
        else:
            logger.warning(f"  - Файл метаданных не найден: {metadata_file}")

        if chunks_file.exists():
            with open(chunks_file, 'r', encoding='utf-8') as f:
                self.chunked_data[language] = json.load(f)
            logger.info(f"  - Загружены чанки из {chunks_file}")
        else:
             logger.warning(f"  - Файл с чанками не найден: {chunks_file}")

    def _get_embedding(self, texts: List[str]) -> np.ndarray:
        """Получает эмбеддинги для списка текстов с помощью Gemini API."""
        try:
            # RETRIEVAL_QUERY используется для запросов, чтобы найти документы
            if len(texts) == 1:
                # Для одного текста API возвращает одиночный вектор
                result = genai.embed_content(
                    model=self.embedding_model_name,
                    content=texts[0],
                    task_type="RETRIEVAL_QUERY"
                )
                embedding = result['embedding']
                return np.array([embedding], dtype='float32')
            else:
                # Для множественных текстов API возвращает список векторов
                all_embeddings = []
                for text in texts:
                    result = genai.embed_content(
                        model=self.embedding_model_name,
                        content=text,
                        task_type="RETRIEVAL_QUERY"
                    )
                    all_embeddings.append(result['embedding'])
                return np.array(all_embeddings, dtype='float32')
        except Exception as e:
            logger.error(f"❌ Ошибка при получении эмбеддинга от Gemini API: {e}", exc_info=True)
            # Возвращаем нулевой вектор, чтобы избежать падения
            dim = 768 # Размерность для text-embedding-004
            return np.zeros((len(texts), dim), dtype='float32')


    def _search_by_vector(self, query_embedding: np.ndarray, language: str, top_k: int, vector_distance_threshold: float = None) -> List[Dict[str, Any]]:
        """Внутренний метод векторного поиска в FAISS."""
        index = self.indices.get(language)
        if not index: return []

        try:
            query_norm = query_embedding.copy().reshape(1, -1)
            faiss.normalize_L2(query_norm)
            distances, indices_found = index.search(query_norm, top_k * 2) # Ищем с запасом
            
            results = []
            metadata_list = self.metadata.get(language, [])
            chunks_map = self.chunked_data.get(language, {})
            
            seen_ids = set()
            
            for i, (dist, idx) in enumerate(zip(distances[0], indices_found[0])):
                if idx < 0: continue

                # Применяем пороговое значение расстояния
                if vector_distance_threshold is not None and dist > vector_distance_threshold:
                    continue


                meta = metadata_list[idx] if isinstance(metadata_list, list) and idx < len(metadata_list) else {}
                book, chapter = meta.get('book'), meta.get('chapter')
                chunk_idx = meta.get('chunk_idx')
                
                # Формируем уникальный ID для дедупликации
                unique_id = f"{book}_{chapter}_{chunk_idx}"
                if unique_id in seen_ids:
                    continue
                seen_ids.add(unique_id)
                
                # Попытка получить полный текст из chunked_data
                text = ""
                if book and chapter and book in chunks_map and chapter in chunks_map[book]:
                    chapter_chunks = chunks_map[book][chapter]
                    if isinstance(chapter_chunks, list) and isinstance(chunk_idx, int):
                        if 0 <= chunk_idx < len(chapter_chunks):
                            text = chapter_chunks[chunk_idx]
                
                if not text:
                    text = meta.get('text_preview', '') + '...'

                results.append({
                    'index': int(idx),
                    'distance': float(dist),
                    'score': float(1.0 / (1.0 + dist)),
                    'text': text,
                    'book': book, 
                    'chapter': chapter, 
                    'verse': None, 
                    'chunk_idx': chunk_idx
                })
                
                if len(results) >= top_k:
                    break

            return results
        except Exception as e:
            logger.error(f"Ошибка при поиске по вектору ({language}): {e}", exc_info=True)
            return []

    def search(
        self, 
        query: str, 
        language: str = 'ru', 
        top_k: int = 5, 
        use_reranking: bool = True,
        expand_query: bool = True,
        vector_distance_threshold: float = None
    ) -> Dict[str, Any]:
        """Основной метод поиска."""
        logger.info(f"🔍 Поиск: '{query}' ({language}, top_k={top_k})")
        if language not in self.indices:
            return {'success': False, 'error': f'Индекс для языка {language} не загружен.'}

        try:
            # 1. Расширение запроса
            query_variants = [query]
            if expand_query:
                expander_method = getattr(QueryExpander, f'expand_query_{language}', None)
                if expander_method:
                    query_variants = expander_method(query)
            
            logger.info(f"   📋 Варианты запроса: {query_variants}")
            
            # 2. Получение эмбеддингов для всех вариантов запроса одним батчем
            variant_embeddings = self._get_embedding(query_variants)
            logger.info(f"   🔢 Получено эмбеддингов: {variant_embeddings.shape}")
            
            # 3. Векторный поиск для каждого варианта
            all_results = []
            for idx, emb in enumerate(variant_embeddings):
                vector_results = self._search_by_vector(emb, language, top_k * 2, vector_distance_threshold)
                logger.debug(f"   🔎 Вариант '{query_variants[idx]}': найдено {len(vector_results)} результатов")
                all_results.extend(vector_results)
            
            # 4. Удаление дубликатов и отбор лучших
            seen_indices = set()
            unique_results = []
            for res in sorted(all_results, key=lambda x: x['score'], reverse=True):
                if res['index'] not in seen_indices:
                    seen_indices.add(res['index'])
                    unique_results.append(res)
            
            top_results = unique_results[:top_k]

            # 5. Переранжирование
            if use_reranking and self.reranker.model:
                docs_to_rerank = [r['text'] for r in top_results]
                reranked_tuples = self.reranker.rerank(query, docs_to_rerank, top_k)
                
                # Сопоставление результатов re-ranker'а с исходными данными
                final_results = []
                for original_idx, score, text in reranked_tuples:
                    original_result = top_results[original_idx]
                    original_result['final_score'] = float(score)
                    final_results.append(original_result)
            else:
                final_results = top_results

            return {
                'success': True,
                'results': final_results,
                'query_variants': query_variants,
                'count': len(final_results)
            }
        
        except Exception as e:
            logger.error(f"❌ Критическая ошибка при поиске: {e}", exc_info=True)
            return {'success': False, 'error': str(e), 'query': query}
