import hashlib
import json
import re
from datetime import datetime, timezone

import anthropic

from config.config import settings
from retrieve import retrieve

with open("questions.json") as f:
    QUESTIONS = json.load(f)

SYSTEM = (
    "You are a precise technical documentation assistant. "
    "Answer questions using ONLY the provided context chunks. "
    "Respond with valid JSON only — no markdown, no text outside the JSON object."
)

MODEL = "claude-haiku-4-5-20251001"
LOG_PATH = "artifacts/llm_calls.jsonl"

client = anthropic.Anthropic(api_key=settings.anthropic_api_key)


def build_prompt(question: str, chunks: list[dict]) -> str:
    context = "\n\n".join(f"[{c['chunk_id']}]\n{c['text']}" for c in chunks)
    return f"""Context:
{context}

Question: {question}

Rules:
- Answer only from the context above; cite every factual claim with chunk IDs like [chunk_001]
- If the context lacks sufficient information, set supported=false and answer exactly: "The knowledge base does not provide enough information to answer this"
- If supported=false, citations must be an empty list
- Do not invent product features, numbers, prices, or policies

Respond with this exact JSON structure:
{{
  "answer": "...",
  "supported": true,
  "citations": ["chunk_001"]
}}"""


def log_llm_call(
    question_id: str,
    prompt: str,
    chunks: list[dict],
    parsed: dict,
) -> None:
    record = {
        "stage": "answer_generation",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "provider": "anthropic",
        "model": MODEL,
        "question_id": question_id,
        "prompt_hash": hashlib.sha256(prompt.encode()).hexdigest(),
        "input_artifacts": {
            "retrieved_chunk_ids": [c["chunk_id"] for c in chunks],
        },
        "output_artifacts": {
            "answer": parsed["answer"],
            "supported": parsed["supported"],
            "citations": parsed["citations"],
        },
    }
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(record) + "\n")


def generate_answer(question: str) -> dict:
    retrieval = retrieve(question, top_k=5)
    chunks = retrieval["retrieved_chunks"]
    prompt = build_prompt(question, chunks)

    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = response.content[0].text.strip()
    raw = re.sub(r"^```(?:json)?\n?", "", raw)
    raw = re.sub(r"\n?```$", "", raw)
    parsed = json.loads(raw)

    log_llm_call(retrieval["id"], prompt, chunks, parsed)

    return {
        "id": retrieval["id"],
        "question": question,
        "answer": parsed["answer"],
        "supported": parsed["supported"],
        "citations": parsed["citations"],
        "retrieved_chunk_ids": [c["chunk_id"] for c in chunks],
    }


# Clear log for this run
open(LOG_PATH, "w").close()

answers = []
for q in QUESTIONS:
    print(f"  {q}")
    answers.append(generate_answer(q))

with open("artifacts/answers.json", "w") as f:
    json.dump(answers, f, indent=2)

print(f"\nGenerated {len(answers)} answers → artifacts/answers.json")
print(f"LLM calls logged      → {LOG_PATH}")
