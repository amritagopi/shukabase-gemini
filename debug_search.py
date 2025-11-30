
import logging
from rag.rag_engine import RAGEngine

# Configure basic logging to console as well
logging.basicConfig(level=logging.INFO)

def debug_search():
    print("Initializing RAG Engine...")
    rag = RAGEngine()
    
    query = "Гададхара Пандит"
    print(f"\nSearching for: {query}")
    
    results = rag.search(query, language='ru', top_k=5)
    
    print("\nSearch Results:")
    if results['success']:
        for res in results['results']:
            print(f"- Score: {res.get('score', 0):.4f} | {res['text'][:100]}...")
    else:
        print(f"Error: {results.get('error')}")

if __name__ == "__main__":
    debug_search()
