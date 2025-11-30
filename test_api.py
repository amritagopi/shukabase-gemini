import requests
import json

print("🧪 Тестирование RAG API напрямую\n")

# Test 1: Health check
print("1️⃣ Проверка доступности API...")
try:
    response = requests.get("http://127.0.0.1:5000/")
    print(f"   ✅ API доступен: {response.status_code}")
except Exception as e:
    print(f"   ❌ API недоступен: {e}")
    exit(1)

# Test 2: Search request
print("\n2️⃣ Отправка поискового запроса...")
url = "http://127.0.0.1:5000/api/search"
payload = {
    "query": "Гададхара Пандит",
    "language": "ru",
    "top_k": 5
}

try:
    response = requests.post(url, json=payload)
    print(f"   Статус: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n3️⃣ Результаты:")
        print(f"   Success: {data.get('success')}")
        print(f"   Количество результатов: {len(data.get('results', []))}")
        
        if data.get('results'):
            print(f"\n4️⃣ Первый результат:")
            first = data['results'][0]
            print(f"   Book: {first.get('book')}")
            print(f"   Chapter: {first.get('chapter')}")
            print(f"   Verse: {first.get('verse')}")
            print(f"   Score: {first.get('final_score', first.get('score'))}")
            print(f"   Text (первые 200 символов):\n   {first.get('text', '')[:200]}...")
            
            print(f"\n5️⃣ Структура данных для frontend:")
            print(f"   ID будет: {first.get('book', 'unknown').replace(' ', '').lower()}.{first.get('chapter')}.{first.get('verse')}")
        else:
            print("   ⚠️ Результаты пусты!")
    else:
        print(f"   ❌ Ошибка: {response.text}")
        
except Exception as e:
    print(f"   ❌ Ошибка запроса: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("Тест завершён")
