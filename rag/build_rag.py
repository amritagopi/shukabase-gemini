#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 ГЛАВНЫЙ СКРИПТ СБОРКИ RAG СИСТЕМЫ

Управляет всеми этапами создания RAG.

ЗАПУСК:
    python rag/build_rag.py
"""

import subprocess
import sys
from pathlib import Path
import time

class RAGBuilder:
    """Строитель RAG системы"""
    
    def __init__(self):
        self.rag_dir = Path("rag")
        self.stages = []
    
    def check_stage(self, name: str, output_files: list) -> bool:
        """Проверяет, завершена ли стадия"""
        all_exist = all(self.rag_dir.joinpath(f).exists() for f in output_files)
        status = "✅ ГОТОВО" if all_exist else "⏳ НУЖНО"
        print(f"  {status}: {name}")
        return all_exist
    
    def print_status(self):
        """Выводит статус всех стадий"""
        print("\n" + "="*70)
        print("📊 СТАТУС СИСТЕМЫ RAG")
        print("="*70 + "\n")
        
        stages = [
            ("Разбиение на чанки", ["chunked_scriptures_ru.json", "chunked_scriptures_en.json"]),
            ("Эмбеддинги", ["embeddings_ru.npy", "embeddings_en.npy"]),
            ("Индекс FAISS", ["faiss_index_ru.bin", "faiss_index_en.bin"]),
        ]
        
        for stage_name, files in stages:
            self.check_stage(stage_name, files)
        
        print()
    
    def run_stage(self, script: str, stage_name: str):
        """Запускает стадию"""
        print(f"\n{'='*70}")
        print(f"▶️  {stage_name}")
        print(f"{'='*70}\n")
        
        script_path = self.rag_dir / script
        
        if not script_path.exists():
            print(f"❌ Файл не найден: {script_path}")
            return False
        
        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=str(self.rag_dir.parent),
                check=False
            )
            
            if result.returncode == 0:
                print(f"\n✅ {stage_name} завершена успешно")
                return True
            else:
                print(f"\n❌ {stage_name} завершена с ошибкой (код: {result.returncode})")
                return False
        
        except Exception as e:
            print(f"❌ Ошибка при запуске {stage_name}: {e}")
            return False
    
    def build_all(self, skip_completed: bool = True):
        """Строит всю систему"""
        
        print("\n" + "🚀 "*20)
        print("🚀 СБОРКА RAG СИСТЕМЫ 🚀")
        print("🚀 "*20 + "\n")
        
        # Этап 1: Чанки
        if skip_completed and self.check_stage("Чанки", ["chunked_scriptures_ru.json", "chunked_scriptures_en.json"]):
            print("  ℹ️  Пропускаю (уже готово)")
        else:
            self.run_stage("chunk_splitter.py", "Этап 1: Разбиение текста на чанки")
        
        # Этап 2: Эмбеддинги
        if skip_completed and self.check_stage("Эмбеддинги", ["embeddings_ru.npy", "embeddings_en.npy"]):
            print("  ℹ️  Пропускаю (уже готово)")
        else:
            self.run_stage("embeddings_minimal.py", "Этап 2: Генерация эмбеддингов")
        
        # Этап 3: FAISS
        if skip_completed and self.check_stage("FAISS", ["faiss_index_ru.bin", "faiss_index_en.bin"]):
            print("  ℹ️  Пропускаю (уже готово)")
        else:
            print("\n⚠️  Для FAISS необходимо запустить отдельный скрипт:")
            print("   python rag/faiss_indexer.py")
        
        self.print_status()
    
    def show_menu(self):
        """Интерактивное меню"""
        
        while True:
            print("\n" + "="*70)
            print("🚀 RAG СИСТЕМА - ГЛАВНОЕ МЕНЮ")
            print("="*70)
            print("\n1. Показать статус")
            print("2. Разбить текст на чанки")
            print("3. Генерировать эмбеддинги")
            print("4. Запустить полную сборку")
            print("5. Выход\n")
            
            choice = input("Выберите опцию (1-5): ").strip()
            
            if choice == "1":
                self.print_status()
            elif choice == "2":
                self.run_stage("chunk_splitter.py", "Разбиение текста на чанки")
            elif choice == "3":
                self.run_stage("embeddings_minimal.py", "Генерация эмбеддингов")
            elif choice == "4":
                self.build_all(skip_completed=True)
            elif choice == "5":
                print("\nДо встречи! 👋")
                break
            else:
                print("❌ Неправильная опция")


def main():
    """Главная функция"""
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "status":
            RAGBuilder().print_status()
        elif sys.argv[1] == "build":
            RAGBuilder().build_all(skip_completed=True)
        elif sys.argv[1] == "menu":
            RAGBuilder().show_menu()
        else:
            print(f"Неизвестная команда: {sys.argv[1]}")
            print("Используйте: python rag/build_rag.py [status|build|menu]")
    else:
        RAGBuilder().show_menu()


if __name__ == "__main__":
    main()
