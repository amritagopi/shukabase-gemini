#!/bin/bash
# Build data archives with books folder included

set -e

echo "🚀 Building Shukabase Data Archives"
echo "===================================="

# Create build directory
BUILD_DIR="builds/data_archives"
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

# --- English Archive ---
echo ""
echo "📦 Building English archive..."
EN_DIR="$BUILD_DIR/shukabase_data_en"
mkdir -p "$EN_DIR"

cp rag/faiss_index_en.bin "$EN_DIR/"
cp rag/faiss_metadata_en.json "$EN_DIR/"
cp rag/chunked_scriptures_en.json "$EN_DIR/"
# BM25 will be regenerated on first run, but include if exists
[ -f rag/bm25_index_en.pkl ] && cp rag/bm25_index_en.pkl "$EN_DIR/"

# Copy books
echo "   Copying English books..."
mkdir -p "$EN_DIR/books"
cp -r public/books/en "$EN_DIR/books/"

echo "   Creating zip..."
cd "$BUILD_DIR"
zip -r shukabase_data_en.zip shukabase_data_en/
cd -
echo "✅ English archive ready"

# --- Russian Archive ---
echo ""
echo "📦 Building Russian archive..."
RU_DIR="$BUILD_DIR/shukabase_data_ru"
mkdir -p "$RU_DIR"

cp rag/faiss_index_ru.bin "$RU_DIR/"
cp rag/faiss_metadata_ru.json "$RU_DIR/"
cp rag/chunked_scriptures_ru.json "$RU_DIR/"
[ -f rag/bm25_index_ru.pkl ] && cp rag/bm25_index_ru.pkl "$RU_DIR/"

# Copy books
echo "   Copying Russian books..."
mkdir -p "$RU_DIR/books"
cp -r public/books/ru "$RU_DIR/books/"

echo "   Creating zip..."
cd "$BUILD_DIR"
zip -r shukabase_data_ru.zip shukabase_data_ru/
cd -
echo "✅ Russian archive ready"

# --- Multilingual Archive ---
echo ""
echo "📦 Building Multilingual archive..."
ALL_DIR="$BUILD_DIR/shukabase_data_multilingual"
mkdir -p "$ALL_DIR"

# Copy both languages
cp rag/faiss_index_en.bin "$ALL_DIR/"
cp rag/faiss_metadata_en.json "$ALL_DIR/"
cp rag/chunked_scriptures_en.json "$ALL_DIR/"
cp rag/faiss_index_ru.bin "$ALL_DIR/"
cp rag/faiss_metadata_ru.json "$ALL_DIR/"
cp rag/chunked_scriptures_ru.json "$ALL_DIR/"
[ -f rag/bm25_index_en.pkl ] && cp rag/bm25_index_en.pkl "$ALL_DIR/"
[ -f rag/bm25_index_ru.pkl ] && cp rag/bm25_index_ru.pkl "$ALL_DIR/"

# Copy all books
echo "   Copying all books..."
mkdir -p "$ALL_DIR/books"
cp -r public/books/en "$ALL_DIR/books/"
cp -r public/books/ru "$ALL_DIR/books/"

echo "   Creating zip..."
cd "$BUILD_DIR"
zip -r shukabase_data_multilingual.zip shukabase_data_multilingual/
cd -
echo "✅ Multilingual archive ready"

# --- Summary ---
echo ""
echo "===================================="
echo "📊 Archive Summary:"
ls -lh "$BUILD_DIR"/*.zip
echo ""
echo "🎉 Done! Upload these to GitHub Releases with tag 'data-v2'"
