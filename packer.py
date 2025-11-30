import os
import fnmatch

# Имя выходного файла
OUTPUT_FILE = "full_project_dump.txt"

# Игнорируем только системные и тяжелые папки
IGNORE_DIRS = {
    '.git', 'node_modules', '__pycache__', 'dist', 'build',
    'venv', 'env', '.idea', '.vscode', 'books'
}

# Игнорируем большие бинарные файлы базы данных, но оставляем JSON с данными
IGNORE_FILES = {
    'package-lock.json', 'yarn.lock', 'full_project_dump.txt',
    'packer.py', 'packer_v2.py',
    'faiss_index.bin', 'faiss_index_en.bin', 'faiss_index_ru.bin'
}

# Читаем .gitignore и добавляем паттерны
ignore_patterns = []
try:
    with open('.gitignore', 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                ignore_patterns.append(line)
except FileNotFoundError:
    pass

def main():
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as outfile:
        outfile.write(f"=== FULL PROJECT DUMP ===\n\n")
        
        for root, dirs, files in os.walk("."):
            # Фильтруем папки
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            dirs[:] = [d for d in dirs if not any(
                (pat.endswith('/') and d == pat[:-1]) or
                fnmatch.fnmatch(d, pat) or
                fnmatch.fnmatch(os.path.join(root, d), pat)
                for pat in ignore_patterns
            )]

            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, ".")

                if file in IGNORE_FILES: continue
                if any(
                    (pat.endswith('/') and rel_path.startswith(pat[:-1] + os.sep)) or
                    fnmatch.fnmatch(file, pat) or
                    fnmatch.fnmatch(rel_path, pat)
                    for pat in ignore_patterns
                ): continue

                # Игнорируем картинки и скомпилированный питон
                if file.endswith(('.png', '.jpg', '.jpeg', '.ico', '.pyc')): continue

                # Игнорируем большие файлы (>10MB)
                if os.path.getsize(file_path) > 10 * 1024 * 1024: continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        content = infile.read()
                        outfile.write(f"--- START OF FILE {rel_path} ---\n")
                        outfile.write(content)
                        outfile.write(f"\n--- END OF FILE {rel_path} ---\n\n")
                        print(f"Packed: {rel_path}")
                except Exception as e:
                    print(f"Skipped (reading error): {rel_path}")

    print(f"\n✅ Готово! Файл {OUTPUT_FILE} создан.")

if __name__ == "__main__":
    main()
