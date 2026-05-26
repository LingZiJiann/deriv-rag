import json

with open("artifacts/answers.json") as f:
    answers = json.load(f)

with open("artifacts/citation_validation.json") as f:
    validation_by_id = {r["id"]: r for r in json.load(f)}

final = [
    {
        "question": a["question"],
        "answer": a["answer"],
        "supported": a["supported"],
        "citations": a["citations"],
        "retrieved_chunk_ids": a["retrieved_chunk_ids"],
        "validation": {
            "passed": validation_by_id[a["id"]]["passed"],
            "issues": validation_by_id[a["id"]]["issues"],
        },
    }
    for a in answers
]

with open("artifacts/final_answers.json", "w") as f:
    json.dump(final, f, indent=2)

print(f"Merged {len(final)} records → artifacts/final_answers.json")
