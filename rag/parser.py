#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 HTML ПАРСЕР ДЛЯ SHUKABASE

Этот модуль извлекает текст из HTML файлов писаний.
"""

from pathlib import Path
from bs4 import BeautifulSoup
import json
from collections import defaultdict

class ScriptureParser:
    """Парсер HTML файлов писаний"""
    
    def __init__(self, cleaned_vedabase_path="cleaned_vedabase"):
        self.base_path = Path(cleaned_vedabase_path)
        self.parsed_data = defaultdict(lambda: defaultdict(dict))
        
    def parse_html_file(self, file_path):
        """
        Парсит один HTML файл и извлекает текст
        
        Args:
            file_path: путь к HTML файлу
            
        Returns:
            dict с извлечённым текстом
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f, 'html.parser')
                
            # Извлекаем основной текст
            text_content = []
            
            # Ищем основные теги с контентом
            for tag in soup.find_all(['p', 'div', 'span']):
                text = tag.get_text(strip=True)
                if text and len(text) > 5:  # Пропускаем короткие строки
                    text_content.append(text)
            
            return {
                'text': ' '.join(text_content),
                'success': True
            }
        except Exception as e:
            return {
                'text': '',
                'success': False,
                'error': str(e)
            }
    
    def parse_all_scriptures(self, language='ru'):
        """
        Парсит все файлы для выбранного языка
        
        Args:
            language: 'ru' или 'en'
            
        Returns:
            dict с распарсенными данными
        """
        lang_dir = self.base_path / language
        
        if not lang_dir.exists():
            print(f"❌ Папка {lang_dir} не найдена!")
            return {}
        
        print(f"\n🔍 Начинаем парсинг {language.upper()} писаний...")
        
        parsed_count = 0
        error_count = 0
        total_chars = 0
        
        # Проходим по всем HTML файлам
        html_files = sorted(lang_dir.rglob("*.html"))
        total_files = len(html_files)
        
        for idx, html_file in enumerate(html_files, 1):
            # Считаем прогресс
            if idx % 1000 == 0:
                print(f"  📄 Обработано {idx}/{total_files} файлов...")
            
            # Получаем относительный путь для ключа
            rel_path = html_file.relative_to(lang_dir)
            book_name = rel_path.parts[0]
            
            # Парсим файл
            result = self.parse_html_file(html_file)
            
            if result['success']:
                self.parsed_data[language][book_name][str(rel_path)] = result['text']
                parsed_count += 1
                total_chars += len(result['text'])
            else:
                error_count += 1
                print(f"  ⚠️  Ошибка парсинга: {rel_path} - {result.get('error', 'Unknown')}")
        
        print(f"\n✅ Парсинг завершён!")
        print(f"  📊 Успешно: {parsed_count} файлов")
        print(f"  ❌ Ошибок: {error_count} файлов")
        print(f"  📈 Всего символов: {total_chars:,}")
        
        return dict(self.parsed_data[language])
    
    def save_to_json(self, output_file, language='ru'):
        """
        Сохраняет распарсенные данные в JSON
        
        Args:
            output_file: путь к выходному файлу
            language: 'ru' или 'en'
        """
        print(f"\n💾 Сохраняю в {output_file}...")
        
        output_path = Path(output_file)
        
        # Преобразуем defaultdict в обычный dict
        data_to_save = dict(self.parsed_data[language])
        for book_name in data_to_save:
            data_to_save[book_name] = dict(data_to_save[book_name])
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=2)
        
        file_size = output_path.stat().st_size / (1024*1024)
        print(f"✅ Файл сохранён! Размер: {file_size:.2f} МБ")


def parse_scriptures_for_language(language='ru', output_file=None):
    """
    Удобная функция для парсинга писаний одного языка
    
    Args:
        language: 'ru' или 'en'
        output_file: путь к выходному файлу (если None, используется default)
    """
    if output_file is None:
        output_file = f"rag/parsed_scriptures_{language}.json"
    # Проверяем, существует ли уже выходной файл
    output_path = Path(output_file)
    if output_path.exists():
        print(f"⏩ {output_file} уже существует. Пропускаю парсинг {language}.")
        return None
    parser = ScriptureParser()
    # Парсим
    parsed = parser.parse_all_scriptures(language=language)
    # Сохраняем
    parser.save_to_json(output_file, language=language)
    return parsed


import sys
if __name__ == "__main__":
    # CLI: python parser.py [ru|en|all]
    langs = []
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ('ru', 'en'):
            langs = [arg]
        else:
            langs = ['ru', 'en']
    else:
        langs = ['ru', 'en']
    for lang in langs:
        parse_scriptures_for_language(language=lang)
