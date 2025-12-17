#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔎 REST API ДЛЯ RAG ПОИСКА

Этот сервер предоставляет API для поиска, используя централизованный RAGEngine.
Поддерживает "Мастер настройки" для первого запуска.

Запуск:
    python rag/rag_api_server.py
"""

import flask
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import logging
import sys
import os
import json
import shutil
import zipfile
import requests
import threading
import time
from pathlib import Path

# --- Sentry Integration ---
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="https://f45f0c9e6cba5042d563be0d77a1b6ca@o4509290473324544.ingest.de.sentry.io/4510551312040016",
    integrations=[FlaskIntegration()],
    send_default_pii=True
)

# --- Настройка логгирования (СРАЗУ) ---
# Определяем путь к логам до всего остального
APP_NAME = "Shukabase"
if getattr(sys, 'frozen', False):
    local_app_data = os.getenv('LOCALAPPDATA')
    if not local_app_data:
         local_app_data = os.path.join(os.path.expanduser("~"), ".shukabase")
    base_path = os.path.join(local_app_data, APP_NAME)
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

log_dir = os.path.join(base_path, "logs")
if not os.path.exists(log_dir):
    try:
        os.makedirs(log_dir, exist_ok=True)
    except:
        pass # Если не можем создать, пишем в stderr

log_file = os.path.join(log_dir, "rag_api_server.log")

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8', mode='a'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --- Добавляем корень проекта в sys.path ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # ⚠️ КРИТИЧЕСКИЙ ИМПОРТ ⚠️
    try:
        from rag.rag_engine import RAGEngine
    except ImportError:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from rag_engine import RAGEngine
except Exception as e:
    logger.critical(f"🔥 FATAL IMPORT ERROR: {e}", exc_info=True)
    # Пытаемся продолжить чтобы сервер запустился и отдал лог, но без движка
    RAGEngine = None 

# --- Константы ---

# ID архива данных
DATA_ARCHIVE_ID = os.environ.get("SHUKABASE_DATA_ID", "1eqZDHhw2HbpaiWydGZXKvTPJf6EIShA0")
DATA_VERSION = 2 # Increment this to force re-download on client updates

DATA_DIR = os.path.join(base_path, "rag_data") if getattr(sys, 'frozen', False) else base_path
CHAT_HISTORY_DIR = os.path.join(base_path, "chat_history")

# --- Глобальные переменные ---
app = Flask(__name__)
CORS(app)
rag_engine_instance = None
init_lock = threading.Lock()

# Состояние процесса установки
setup_state = {
    "is_downloading": False,
    "progress": 0,
    "status": "idle", # idle, downloading, extracting, completed, error
    "error": None,
    "current_file": ""
}

# --- Функции для скачивания данных ---

# ... (Previous download functions remain, but we need to update background_download_task to write version)

# --- API Endpoints ---

@app.route('/api/setup/status', methods=['GET'])
def get_setup_status():
    is_installed = False
    
    if os.path.exists(DATA_DIR):
        # 1. Check for critical files (Index AND JSON)
        has_index = any(f.startswith("faiss_index") for f in os.listdir(DATA_DIR))
        has_json = any(f.startswith("chunked_scriptures") for f in os.listdir(DATA_DIR))
        
        # 2. Check Data Version
        version_file = os.path.join(DATA_DIR, "data_version.txt")
        is_version_match = False
        if os.path.exists(version_file):
            try:
                with open(version_file, 'r') as f:
                    v = int(f.read().strip())
                    if v >= DATA_VERSION:
                        is_version_match = True
            except:
                pass
        
        # Combined check: Must have files AND correct version
        if has_index and has_json and is_version_match:
            is_installed = True
            
    return jsonify({
        "installed": is_installed,
        "engine_ready": rag_engine_instance is not None,
        "setup_state": setup_state
    })

@app.route('/api/setup/download', methods=['POST'])
def start_download():
    if setup_state["is_downloading"]:
        return jsonify({"error": "Download already in progress"}), 400
        
    lang = request.json.get('language', 'all')
    thread = threading.Thread(target=background_download_task, args=(lang,))
    thread.start()
    
    return jsonify({"success": True, "message": "Download started"})

@app.route('/api/search', methods=['POST'])
def search():
    if rag_engine_instance is None:
        # Пытаемся инициализировать, если вдруг файлы появились
        if not initialize_engine():
            return jsonify({'success': False, 'error': 'Knowledge base not loaded. Please complete setup.'}), 503

    try:
        data = request.json
        query = data.get('query', '').strip()
        language = data.get('language', 'ru')
        top_k = int(data.get('top_k', 10))
        
        if not query:
            return jsonify({'success': False, 'error': 'Empty query'}), 400

        search_results = rag_engine_instance.search(
            query=query,
            language=language,
            top_k=top_k,
            api_key=data.get('api_key') # Pass API key from request
        )
        return jsonify(search_results), 200
    except Exception as e:
        logger.error(f"Search error: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'engine_initialized': rag_engine_instance is not None
    }), 200

# --- Остальные эндпоинты (conversations) без изменений ---
@app.route('/api/conversations', methods=['GET'])
def get_conversations():
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
                except Exception:
                    pass
        conversations.sort(key=lambda x: x.get('createdAt', ''), reverse=True)
        return jsonify(conversations)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/conversations/<string:conversation_id>', methods=['GET'])
def get_conversation_by_id(conversation_id):
    filepath = os.path.join(CHAT_HISTORY_DIR, f"{conversation_id}.json")
    if not os.path.exists(filepath):
        return jsonify({'error': 'Not found'}), 404
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/conversations', methods=['POST'])
def save_conversation():
    try:
        data = request.json
        conversation_id = data.get('id')
        if not os.path.exists(CHAT_HISTORY_DIR):
            os.makedirs(CHAT_HISTORY_DIR, exist_ok=True)
        filepath = os.path.join(CHAT_HISTORY_DIR, f"{conversation_id}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return jsonify({'success': True, 'id': conversation_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/conversations/<string:conversation_id>', methods=['DELETE'])
def delete_conversation(conversation_id):
    filepath = os.path.join(CHAT_HISTORY_DIR, f"{conversation_id}.json")
    if os.path.exists(filepath):
        os.remove(filepath)
        return jsonify({'success': True})
    return jsonify({'error': 'Not found'}), 404

@app.route('/books/<path:filename>')
def serve_books(filename):
    try:
        # DATA_DIR typically contains the 'books' folder if extracted correctly
        # We serve directly from DATA_DIR to handle /books/en/... structure
        # If the request is /books/en/sb/1/index.html, filename will be en/sb/1/index.html
        # So we look in DATA_DIR/books/filename
        books_dir = os.path.join(DATA_DIR, 'books')
        if not os.path.exists(books_dir):
             # Fallback: maybe DATA_DIR IS the books dir?
             pass
        return flask.send_from_directory(books_dir, filename)
    except Exception as e:
        logger.error(f"Error serving book file {filename}: {e}")
        return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    logger.info("="*80)
    logger.info(f"🚀 Shukabase AI Server Starting. Data dir: {DATA_DIR}")
    
    # ВАЖНО: Выводим этот статус, чтобы Rust понял, что сервер жив
    print("STATUS: SERVER_STARTED", flush=True)

    # Инициализируем в фоне, чтобы не задерживать старт сервера и сплэша
    threading.Thread(target=initialize_engine, daemon=True).start()
    
    app.run(host='0.0.0.0', port=5000, debug=False)