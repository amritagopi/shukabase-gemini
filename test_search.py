import requests
import json

def test_search(query, top_k=3):
    """Тестирование поиска с подробным выводом"""
    print(f"\n{'='*80}")
    print(f"ЗАПРОС: {query}")
    print(f"{'='*80}\n")
    
    response = requests.post(
        'http://localhost:5000/api/search',
        json={
            'query': query,
            'language': 'ru',
            'top_k': top_k
        }
    )
    
    data = response.json()
    
    if not data.get('success'):
        print(f"❌ Ошибка: {data.get('error')}")
        return
    
    print(f"✅ Найдено результатов: {data.get('count', 0)}")
    print(f"📝 Варианты запроса: {data.get('query_variants', [])}\n")
    
    for i, result in enumerate(data.get('results', []), 1):
        print(f"\n{'─'*80}")
        print(f"Результат #{i}")
        print(f"{'─'*80}")
        print(f"📚 Книга: {result.get('book')}")
        print(f"📖 Глава: {result.get('chapter')}")
        print(f"🎯 Score: {result.get('final_score', result.get('score')):.4f}")
        print(f"📏 Distance: {result.get('distance', 0):.4f}")
        print(f"\n📄 Текст (первые 300 символов):")
        print(f"{result.get('text', '')[:300]}...")
        print()

if __name__ == "__main__":
    # Примеры запросов для тестирования
    test_queries = [
        "душа",
        "Кришна",
        "что такое душа",
        "как достичь освобождения",
        "карма",
    ]
    
    for query in test_queries:
        test_search(query, top_k=2)
        input("\nНажмите Enter для следующего запроса...")
