# deriv-test — RAG Pipeline

A Retrieval-Augmented Generation pipeline that answers natural-language questions against a small corpus of Markdown documentation. Each step runs as an isolated script orchestrated by `main.py`.

## How it works

```
docs/*.md → chunk → embed (Milvus Lite) → retrieve → generate (Claude Haiku) → validate → merge
```

1. **Chunk** — splits docs on `##` headings into section-level chunks
2. **Embed** — encodes chunks with `all-MiniLM-L6-v2` and stores them in a local Milvus vector index (HNSW/cosine)
3. **Generate** — for each question, retrieves top-5 chunks and calls Claude Haiku to produce a JSON answer with citations
4. **Validate** — deterministically checks that citations are grounded (chunk membership, numeric claims)
5. **Merge** — joins answers and validation results into a single output file

## Setup

```bash
# requires Python 3.13+
uv sync

# add your Anthropic API key
echo "ANTHROPIC_API_KEY=sk-..." > .env
```

## Run

```bash
python main.py
```

Outputs a summary table and writes all artifacts to `artifacts/`.

## Output artifacts

| File | Contents |
|------|----------|
| `artifacts/chunks.json` | Section-level text chunks with char offsets |
| `artifacts/answers.json` | LLM answers with citations and retrieved chunk IDs |
| `artifacts/llm_calls.jsonl` | Audit log of every LLM call (prompt hash, I/O artifact IDs) |
| `artifacts/citation_validation.json` | Per-answer pass/fail with issue descriptions |
| `artifacts/final_answers.json` | Denormalized final output joining answers and validation |

## Customising questions

Edit `questions.json` — it's a plain JSON array of question strings.

## Dependencies

- [`anthropic`](https://github.com/anthropics/anthropic-sdk-python) — Claude API
- [`sentence-transformers`](https://www.sbert.net/) — local embedding model
- [`pymilvus[milvus-lite]`](https://milvus.io/docs/milvus_lite.md) — embedded vector store (no server needed)
- [`pydantic-settings`](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) — `.env` config

See [DESIGN.md](DESIGN.md) for a full architecture walkthrough.
