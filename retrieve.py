import json
from uuid import uuid4

from pymilvus import MilvusClient
from sentence_transformers import SentenceTransformer

COLLECTION = "chunks"
DB_PATH = "data/milvus.db"
MODEL_NAME = "all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)
client = MilvusClient(DB_PATH)
client.load_collection(COLLECTION)


def retrieve(question: str, top_k: int = 5) -> dict:
    embedding = model.encode([question])[0].tolist()
    results = client.search(
        COLLECTION,
        [embedding],
        limit=top_k,
        output_fields=["chunk_id", "doc_id", "text"],
    )
    return {
        "id": str(uuid4()),
        "question": question,
        "retrieved_chunks": [
            {
                "chunk_id": hit["entity"]["chunk_id"],
                "doc_id": hit["entity"]["doc_id"],
                "score": hit["distance"],
                "text": hit["entity"]["text"],
            }
            for hit in results[0]
        ],
    }


if __name__ == "__main__":
    result = retrieve("How to cancel plans")
    print(json.dumps(result, indent=2))
