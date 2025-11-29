# coding: utf-8
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import json

def test_relevance(query):
    """Тестирует релевантность результатов поиска"""
    print(f"\n{'='*100}")
    print(f"ТЕСТ РЕЛЕВАНТНОСТИ: {query}")
    print(f"{'='*100}\n")
    
    response = requests.post(
        'http://localhost:5000/api/search',
        json={'query': query, 'language': 'ru', 'top_k': 3}
    )
    
    data = response.json()
    
    if not data.get('success'):
        print(f"❌ Ошибка: {data.get('error')}")
        return
    
    print(f"✅ Найдено: {data.get('count', 0)} результатов")
    print(f"📝 Варианты запроса: {', '.join(data.get('query_variants', []))}\n")
    
    for i, r in enumerate(data.get('results', []), 1):
        print(f"\n{'─'*100}")
        print(f"РЕЗУЛЬТАТ #{i}")
        print(f"{'─'*100}")
        print(f"📍 Источник: {r.get('book')} / {r.get('chapter')}")
        print(f"🎯 Final Score: {r.get('final_score', 'N/A'):.4f}" if isinstance(r.get('final_score'), (int, float)) else f"🎯 Score: {r.get('score', 0):.4f}")
        print(f"📏 Distance: {r.get('distance', 0):.4f}")
        print(f"\n📄 ТЕКСТ:")
        text = r.get('text', '')
        # Показываем первые 500 символов
        preview = text[:500] if len(text) > 500 else text
        print(preview)
        if len(text) > 500:
            print(f"\n... (всего {len(text)} символов)")
    
    print(f"\n{'='*100}\n")
    
    # Оценка релевантности
    print("❓ РЕЛЕВАНТНЫ ЛИ РЕЗУЛЬТАТЫ ЗАПРОСУ?")
    print(f"   Запрос: '{query}'")
    print(f"   Проверьте, содержат ли тексты выше информацию о: {query}")
    print(f"\n{'='*100}\n")

if __name__ == "__main__":
    test_queries = [
        "что такое душа",
        "Кришна",
        "карма и перевоплощение",
    ]
    
    for q in test_queries:
        test_relevance(q)
        print("\n" * 2)
