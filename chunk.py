import json
import re


def chunk_documents(documents: list[dict]) -> list[dict]:
    chunks = []
    chunk_num = 1

    for doc in documents:
        doc_id = doc["doc_id"]
        text = doc["text"]

        section_starts = [m.start() + 1 for m in re.finditer(r"\n## ", text)]

        for i, start in enumerate(section_starts):
            end = section_starts[i + 1] if i + 1 < len(section_starts) else len(text)
            chunks.append(
                {
                    "chunk_id": f"chunk_{chunk_num:03d}",
                    "doc_id": doc_id,
                    "text": text[start:end],
                    "start_char": start,
                    "end_char": end,
                }
            )
            chunk_num += 1

    return chunks


with open("artifacts/documents.json") as f:
    documents = json.load(f)

chunks = chunk_documents(documents)

with open("artifacts/chunks.json", "w") as f:
    json.dump(chunks, f, indent=2)

print(f"Created {len(chunks)} chunks → artifacts/chunks.json")
