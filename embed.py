import json

from pymilvus import DataType, MilvusClient
from sentence_transformers import SentenceTransformer

COLLECTION = "chunks"
DB_PATH = "data/milvus.db"
MODEL_NAME = "all-MiniLM-L6-v2"
DIM = 384

model = SentenceTransformer(MODEL_NAME)

with open("artifacts/chunks.json") as f:
    chunks = json.load(f)

texts = [c["text"] for c in chunks]
embeddings = model.encode(texts, show_progress_bar=True)

client = MilvusClient(DB_PATH)

if client.has_collection(COLLECTION):
    client.drop_collection(COLLECTION)

schema = MilvusClient.create_schema()
schema.add_field("chunk_id", DataType.VARCHAR, max_length=50, is_primary=True)
schema.add_field("doc_id", DataType.VARCHAR, max_length=50)
schema.add_field("text", DataType.VARCHAR, max_length=65535)
schema.add_field("start_char", DataType.INT64)
schema.add_field("end_char", DataType.INT64)
schema.add_field("embedding", DataType.FLOAT_VECTOR, dim=DIM)

index_params = client.prepare_index_params()
index_params.add_index(
    "embedding",
    index_type="HNSW",
    metric_type="COSINE",
    params={"M": 16, "efConstruction": 64},
)

client.create_collection(COLLECTION, schema=schema, index_params=index_params)

data = [
    {**chunk, "embedding": emb.tolist()}
    for chunk, emb in zip(chunks, embeddings)
]
client.insert(COLLECTION, data)
print(f"Inserted {len(data)} chunks → {DB_PATH}")
