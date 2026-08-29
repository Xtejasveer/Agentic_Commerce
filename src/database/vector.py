import chromadb
from src.config import settings

class VectorDatabase:
    def __init__(self):
        # Initialize persistent local storage for embeddings
        self.client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
        self.collection = self.client.get_or_create_collection(
            name="merchant_catalog",
            metadata = {"hnsw:space" : "cosine"},
        )

    def add_products(self, products: list[dict]):
        """
        Ingests structured product dictionaries into the vector database.
        Each product must have : product_id, name, description, price_inr,
        stock_quantity, category
        """
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


    def search(
        self,
        query_string: str,
        n_results : int=5,
        max_price: float | None = None,
        min_price: float | None = None,
        category: str |None = None,
    ) -> list[dict]:
        """Performs semantic similarity search and returns structured results.
        Applies optional price and category post-filters."""

        where_clauses =[]

        if category:
            where_clauses.append({"category": {"$eq":category.lower()}})
        if max_price is not None:
            where_clauses.append({"price_inr" : {"$lte" : max_price}})
        if min_price is not None:
            where_clauses.append({"price_inr" : {"$gte" : min_price}})

        where = None

        if len(where_clauses) ==1 :
            where = where_clauses[0]
        elif len(where_clauses) > 1:
            where = {"$and" : where_clauses}

        query_kwargs = {
            "query_texts" : [query_string],
            "n_results": min(n_results, self.collection.count() or 1 ),
        }
        if where :
            query_kwargs["where"] = where

        raw = self.collection.query(**query_kwargs)

        results =[]
        if not raw["ids"] or not raw["ids"][0]:
            return results
        for i, product_id in enumerate(raw["ids"][0]):
            metadata = raw["metadatas"][0][i]
            distance = raw["distances"][0][i] if raw.get("distances") else None

            similarity = round(1- distance, 4) if distance is not None else None

            results.append(
                {
                    "product_id" :product_id,
                    "name" : metadata.get("name"),
                    "price_inr": metadata.get("price_inr"),
                    "stock_quantity":metadata.get("stock_quantity"),
                    "category" : metadata.get("category"),
                    "similarity_score" : similarity,
                }
            )
        return results

    def get_product_by_id(self, product_id: str) -> dict | None:
        """Fetch a single product by its exact ID."""
        result = self.collection.get(ids = [product_id], include = ["metadatas", "documents"])
        if not result["ids"]:
            return None

        metadata = result["metadatas"][0]
        return {
            "product_id": product_id,
            "name": metadata.get("name"),
            "price_inr": metadata.get("price_inr"),
            "stock_quantity" : metadata.get("stock_quantity"),
            "category":metadata.get("category"),
        }
    def update_stock(self, product_id: str, new_stock: int):
        """Update the stock quantity metadata for a product."""
        existing = self.collection.get(ids = [product_id], include = ["metadatas", "documents"])
        if not existing["ids"]:
            return 

        metadata = existing["metadatas"][0]
        metadata["stock_quantity"] = new_stock
        self.collection.update(ids = [product_id], metadatas=[metadata])

    def delete_all(self):
        """Wipe and recreate the collection — used for re-seeding."""
        self.client.delete_collection("merchant_catalog")
        self.collection = self.client.get_or_create_collection(
            name="merchant_catalog",
            metadata={"hnsw:space": "cosine"},
        )

vector_db = VectorDatabase()