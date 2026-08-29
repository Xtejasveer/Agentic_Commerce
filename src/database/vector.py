import chromadb
from src.config import settings

class VectorDatabase:
    def __init__(self):
        # Initialize persistent local storage for embeddings
        self.client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
        self.collection = self.client.get_or_create_collection(name="merchant_catalog")

    def add_products(self, products: list[dict]):
        """Ingests structured product dictionaries into the vector database."""
        ids = [p["product_id"] for p in products]
        documents = [p["description"] for p in products]
        metadatas = [{
            "name": p["name"],
            "price_inr": p["price_inr"],
            "stock_quantity": p["stock_quantity"]
        } for p in products]

        self.collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )

    def search(self, query_string: str, n_results: int = 3):
        """Performs semantic similarity matching for external agent queries."""
        results = self.collection.query(
            query_texts=[query_string],
            n_results=n_results
        )
        return results

vector_db = VectorDatabase()