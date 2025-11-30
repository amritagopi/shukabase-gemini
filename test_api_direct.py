import requests
import json

# Test the RAG API endpoint
url = "http://127.0.0.1:5000/api/search"
payload = {
    "query": "Гададхара Пандит",
    "language": "ru",
    "top_k": 5
}

print(f"Отправка запроса: {payload}")
response = requests.post(url, json=payload)

print(f"\nСтатус: {response.status_code}")
print(f"\nЗаголовки ответа: {dict(response.headers)}")

if response.status_code == 200:
    data = response.json()
    print(f"\nКоличество результатов: {len(data.get('results', []))}")
    print(f"\nПервые 3 результата:")
    for i, result in enumerate(data.get('results', [])[:3], 1):
        print(f"\n--- Результат {i} ---")
        print(f"Book: {result.get('book')}")
        print(f"Chapter: {result.get('chapter')}")
        print(f"Score: {result.get('score', result.get('final_score', 'N/A'))}")
        print(f"Text preview: {result.get('text', '')[:150]}...")
else:
    print(f"\nОшибка: {response.text}")
