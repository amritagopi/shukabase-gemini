#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔎 REST API ДЛЯ RAG ПОИСКА

Этот сервер предоставляет API для поиска, используя централизованный RAGEngine.

Запуск:
    python rag/rag_api_server.py
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import sys
import os
import json
from datetime import datetime

# Добавляем корень проекта в sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.rag_engine import RAGEngine

# --- Константы ---
CHAT_HISTORY_DIR = "chat_history"

# --- Настройка логгирования ---
log_file = "rag_api_server.log"
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --- Глобальные переменные ---
app = Flask(__name__)
CORS(app)  # Разрешаем CORS для всех доменов
rag_engine_instance = None

# --- Инициализация ---
def initialize_engine():
    """Инициализирует RAGEngine."""
    global rag_engine_instance
    if rag_engine_instance is None:
        logger.info("🧠 Инициализация RAGEngine...")
        try:
            # RAGEngine теперь сам заботится о загрузке ключа API
            rag_engine_instance = RAGEngine(languages=['ru', 'en'])
            logger.info("✅ RAGEngine успешно инициализирован.")
        except Exception as e:
            logger.critical(f"❌ Не удалось инициализировать RAGEngine: {e}", exc_info=True)
            # В случае критической ошибки сервер не сможет работать
            rag_engine_instance = None 

# --- Эндпоинты API ---

@app.route('/api/search', methods=['POST'])
def search():
    """
    Основной эндпоинт для поиска.
    Принимает JSON: {"query": "...", "language": "ru|en", "top_k": 5}
    """
    if rag_engine_instance is None:
        return jsonify({'success': False, 'error': 'RAG Engine не инициализирован.'}), 503

    try:
        data = request.json
        query = data.get('query', '').strip()
        language = data.get('language', 'ru')
        top_k = int(data.get('top_k', 10))
        
        logger.info(f"📥 Поисковый запрос: query='{query}', lang='{language}', top_k={top_k}")

        if not query:
            return jsonify({'success': False, 'error': 'Пустой запрос'}), 400
        if language not in rag_engine_instance.languages:
            return jsonify({'success': False, 'error': f'Язык {language} не поддерживается'}), 400

        # Используем наш централизованный RAGEngine
        # Получаем параметры из запроса (по умолчанию включены для лучшей релевантности)
        use_reranking = data.get('use_reranking', True)
        expand_query = data.get('expand_query', True)
        vector_distance_threshold = data.get('vector_distance_threshold', None)
        
        search_results = rag_engine_instance.search(
            query=query,
            language=language,
            top_k=top_k,
            use_reranking=use_reranking,
            expand_query=expand_query,
            vector_distance_threshold=vector_distance_threshold
        )
        
        return jsonify(search_results), 200

    except Exception as e:
        logger.error(f"❌ Ошибка в эндпоинте /api/search: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Внутренняя ошибка сервера'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Проверка состояния сервера и RAGEngine."""
    if rag_engine_instance:
        status = {
            'status': 'healthy',
            'engine_status': 'initialized',
            'loaded_languages': list(rag_engine_instance.indices.keys())
        }
        return jsonify(status), 200
    else:
        status = {
            'status': 'unhealthy',
            'engine_status': 'not_initialized',
            'error': 'RAGEngine failed to initialize. Check logs.'
        }
        return jsonify(status), 503

@app.route('/api/conversations', methods=['GET'])
def get_conversations():
    """Возвращает список сохраненных переписок."""
    if not os.path.exists(CHAT_HISTORY_DIR):
        return jsonify([])

    conversations = []
    try:
        for filename in os.listdir(CHAT_HISTORY_DIR):
            if filename.endswith('.json'):
                filepath = os.path.join(CHAT_HISTORY_DIR, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        conversations.append({
                            'id': data.get('id'),
                            'title': data.get('title'),
                            'createdAt': data.get('createdAt')
                        })
                except (json.JSONDecodeError, IOError) as e:
                    logger.warning(f"Could not read or parse conversation file {filename}: {e}")
        
        # Sort by createdAt date, newest first
        conversations.sort(key=lambda x: x.get('createdAt', ''), reverse=True)
        
        return jsonify(conversations)

    except Exception as e:
        logger.error(f"Error listing conversations: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Could not list conversations'}), 500

@app.route('/api/conversations/<string:conversation_id>', methods=['GET'])
def get_conversation_by_id(conversation_id):
    """Возвращает полную переписку по ID."""
    filepath = os.path.join(CHAT_HISTORY_DIR, f"{conversation_id}.json")
    if not os.path.exists(filepath):
        return jsonify({'success': False, 'error': 'Conversation not found'}), 404

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error reading conversation {conversation_id}: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Could not read conversation file'}), 500

@app.route('/api/conversations', methods=['POST'])
def save_conversation():
    """Сохраняет новую или обновляет существующую переписку."""
    try:
        data = request.json
        conversation_id = data.get('id')
        if not conversation_id:
            return jsonify({'success': False, 'error': 'Conversation ID is required'}), 400

        filepath = os.path.join(CHAT_HISTORY_DIR, f"{conversation_id}.json")
        
        # Ensure all required fields are present
        if 'title' not in data or 'createdAt' not in data or 'messages' not in data:
            return jsonify({'success': False, 'error': 'Missing required conversation fields (title, createdAt, messages)'}), 400

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        logger.info(f"💾 Conversation '{conversation_id}' saved successfully.")
        return jsonify({'success': True, 'id': conversation_id})

    except Exception as e:
        logger.error(f"Error saving conversation: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Could not save conversation'}), 500

@app.route('/api/conversations/<string:conversation_id>', methods=['DELETE'])
def delete_conversation(conversation_id):
    """Удаляет переписку по ID."""
    filepath = os.path.join(CHAT_HISTORY_DIR, f"{conversation_id}.json")
    if not os.path.exists(filepath):
        return jsonify({'success': False, 'error': 'Conversation not found'}), 404

    try:
        os.remove(filepath)
        logger.info(f"🗑️ Conversation '{conversation_id}' deleted successfully.")
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error deleting conversation {conversation_id}: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Could not delete conversation file'}), 500


# --- Запуск сервера ---
if __name__ == '__main__':
    # Ensure chat history directory exists
    if not os.path.exists(CHAT_HISTORY_DIR):
        os.makedirs(CHAT_HISTORY_DIR)
        
    initialize_engine() # Инициализируем движок при старте
    if rag_engine_instance:
        logger.info("="*80)
        logger.info("🚀 RAG API Server запущен на http://localhost:5000")
        logger.info("   Логи сохраняются в rag_api_server.log")
        logger.info("="*80)
        app.run(host='0.0.0.0', port=5000, debug=False)
    else:
        logger.critical("="*80)
        logger.critical("❌ RAG API Server НЕ МОЖЕТ БЫТЬ ЗАПУЩЕН из-за ошибки инициализации RAGEngine.")
        logger.critical("   Пожалуйста, проверьте файл логов rag_api_server.log и конфигурацию, особенно GEMINI_API_KEY.")
        logger.critical("="*80)