# DESIGN.md — RAG Pipeline Architecture

## Overview

This project is a **Retrieval-Augmented Generation (RAG) pipeline** that answers natural-language questions against a small corpus of Markdown documentation. It is implemented as a series of single-purpose Python scripts orchestrated by `main.py`.

The pipeline ingests Markdown docs, chunks and embeds them into a vector store, retrieves relevant context per question, generates LLM answers with citations, validates those citations, and merges everything into a final output artifact.

---

## Data Flow

```
docs/*.md
    │
    ▼
artifacts/documents.json          ← pre-loaded raw doc corpus
    │
    ▼  chunk.py
artifacts/chunks.json             ← section-level text chunks
    │
    ▼  embed.py
data/milvus.db                    ← vector index (Milvus Lite, HNSW/COSINE)
    │
    ├─── retrieve.py (used inline by generate.py)
    │
questions.json ──────────────────────────────┐
    │                                         │
    ▼  generate.py                            │
artifacts/answers.json            ← LLM answers with citations
artifacts/llm_calls.jsonl         ← audit log of every LLM call
    │
    ▼  validate.py
artifacts/citation_validation.json ← per-answer pass/fail with issues
    │
    ▼  merge.py
artifacts/final_answers.json      ← denormalized, ready-to-consume output
```

---

## Pipeline Steps

### 1. Document Loading (`artifacts/documents.json`)

The corpus is pre-materialized as a JSON array. Each document has:

```json
{ "doc_id": "doc_001", "path": "docs/pricing.md", "text": "..." }
```

The five source documents cover: pricing, API limits, authentication, webhooks, and data retention.

### 2. Chunking (`chunk.py`)

Splits each document on `## ` H2 headings using a regex. Each chunk gets a sequential `chunk_id` (`chunk_001`, `chunk_002`, …) and records `start_char`/`end_char` offsets back to the source document.

No overlap or sliding-window strategy is used — chunks are section-aligned.

### 3. Embedding + Indexing (`embed.py`)

- **Model**: `all-MiniLM-L6-v2` via `sentence-transformers` (384-dimensional vectors)
- **Vector store**: Milvus Lite (local file at `data/milvus.db`)
- **Index**: HNSW with `M=16`, `efConstruction=64`, cosine similarity metric
- Drops and recreates the `chunks` collection on every run (full rebuild, no incremental updates)
- Stores chunk text alongside the vector so retrieval returns full text without a second lookup

### 4. Retrieval (`retrieve.py`)

Encodes a query string with the same `all-MiniLM-L6-v2` model and runs an approximate nearest-neighbour search returning the top-k (default 5) chunks by cosine similarity. Returns chunk text, IDs, doc IDs, and similarity scores.

`retrieve.py` is also importable as a module — `generate.py` calls `retrieve()` directly.

### 5. Answer Generation (`generate.py`)

- **Model**: `claude-haiku-4-5-20251001` via the Anthropic SDK
- Retrieves top-5 chunks per question, builds a structured prompt that injects chunks as numbered context blocks, and instructs the model to respond in strict JSON with `answer`, `supported`, and `citations` fields
- **Hallucination guardrail**: the model is instructed to set `supported=false` and return a fixed refusal string if context is insufficient; it must never invent numbers, prices, or features
- Writes an audit log to `artifacts/llm_calls.jsonl` — one JSONL record per call, including a SHA-256 hash of the prompt and the input/output artifact IDs
- API key is loaded via `config/config.py` using `pydantic-settings` from a `.env` file

### 6. Citation Validation (`validate.py`)

Purely deterministic, no LLM. Enforces four rules on every answer:

| Rule | Check |
|------|-------|
| 1 | Every cited chunk ID must be in the answer's `retrieved_chunk_ids` set |
| 2 | `supported=true` requires at least one citation |
| 3 | `supported=false` requires an empty citations list |
| 4 | Every number in the answer text must appear verbatim in the cited chunk text (numeric grounding) |

Failures are collected as human-readable issue strings and written to `citation_validation.json`.

### 7. Merge (`merge.py`)

Joins `answers.json` and `citation_validation.json` by UUID, producing a flat `final_answers.json` where every record contains the question, answer, citation metadata, and validation result together.

### 8. Orchestration (`main.py`)

Runs each step as a subprocess (`subprocess.run`), stopping the pipeline on first failure (`returncode != 0`). After all steps succeed, loads the artifacts and prints a summary table.

---

## Project Layout

```
deriv_test/
├── main.py                  # pipeline orchestrator
├── chunk.py                 # step 2: document chunking
├── embed.py                 # step 3: embedding + vector indexing
├── retrieve.py              # step 4: vector retrieval (also a library module)
├── generate.py              # step 5: LLM answer generation
├── validate.py              # step 6: citation validation
├── merge.py                 # step 7: output merging
├── config/
│   └── config.py            # pydantic-settings env config
├── docs/
│   ├── pricing.md
│   ├── api-limits.md
│   ├── authentication.md
│   ├── webhooks.md
│   └── data-retention.md
├── questions.json           # input: list of questions to answer
├── artifacts/               # all pipeline outputs
│   ├── documents.json
│   ├── chunks.json
│   ├── answers.json
│   ├── llm_calls.jsonl
│   ├── citation_validation.json
│   └── final_answers.json
└── data/
    └── milvus.db/           # Milvus Lite vector store on disk
```

---

## Dependencies

| Library | Role |
|---------|------|
| `anthropic` | Claude LLM API client |
| `sentence-transformers` | Local embedding model (`all-MiniLM-L6-v2`) |
| `pymilvus[milvus-lite]` | Local vector store (no server required) |
| `pydantic-settings` | `.env`-backed config |

Python ≥ 3.13 required.

---

## Design Decisions

**Subprocess orchestration over direct imports** — each pipeline step runs as an isolated process. A crash or bad import in one step cannot corrupt the state of others, and stdout from each step is cleanly separable.

**Full rebuild on every run** — the vector index is dropped and recreated in `embed.py`. This keeps the pipeline stateless and reproducible at the cost of speed; suitable for a small corpus.

**Same model for query and document embedding** — `retrieve.py` and `embed.py` both load `all-MiniLM-L6-v2` independently. They must stay in sync: if the indexing model changes, retrieval must change too.

**Deterministic citation validation** — no LLM is used for validation, which makes the check fast, cheap, and repeatable. The numeric grounding rule (Rule 4) catches the most common class of hallucination without requiring a second model call.

**Audit logging** — `llm_calls.jsonl` captures a prompt hash, chunk IDs in, and structured output for every generation call. This enables offline reproducibility checks without re-running the pipeline.
