#!/bin/bash

echo "========================================================"
echo " SHUKABASE AI - MASTER TEST RUNNER (Bash)"
echo "========================================================"
echo ""

echo "[1/2] Running BACKEND Tests (Python)..."
echo "----------------------------------------"
# Try to use venv python if available, otherwise fallback to python
if [ -f "./venv/Scripts/python" ]; then
    ./venv/Scripts/python -m pytest rag/tests
elif [ -f "./venv/bin/python" ]; then
    ./venv/bin/python -m pytest rag/tests
else
    python -m pytest rag/tests
fi

if [ $? -ne 0 ]; then
    echo "[ERROR] Backend tests FAILED!"
    exit 1
else
    echo "[SUCCESS] Backend tests PASSED."
fi
echo ""

echo "[2/2] Running FRONTEND Tests (Vitest)..."
echo "----------------------------------------"
npm test

if [ $? -ne 0 ]; then
    echo "[ERROR] Frontend tests FAILED!"
    exit 1
else
    echo "[SUCCESS] Frontend tests PASSED."
fi
echo ""

echo "========================================================"
echo " ALL TESTS PASSED SUCCESSFULLY!"
echo "========================================================"
exit 0
