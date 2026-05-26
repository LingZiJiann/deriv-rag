import json
import re


def extract_numbers(text: str) -> list[str]:
    return re.findall(r"\b\d[\d,.]*\b", text)


with open("artifacts/answers.json") as f:
    answers = json.load(f)

with open("artifacts/chunks.json") as f:
    chunk_text_by_id = {c["chunk_id"]: c["text"] for c in json.load(f)}

results = []

for answer in answers:
    issues = []
    retrieved_ids = set(answer.get("retrieved_chunk_ids", []))
    citations = answer.get("citations", [])
    supported = answer.get("supported", False)
    answer_text = answer.get("answer", "")

    # Rule 1: every citation must be in retrieved chunks
    for cid in citations:
        if cid not in retrieved_ids:
            issues.append(f"Citation {cid} not in retrieved chunks")

    # Rule 2: supported=true requires at least one citation
    if supported and len(citations) == 0:
        issues.append("supported=true but citations list is empty")

    # Rule 3: supported=false requires empty citations
    if not supported and len(citations) > 0:
        issues.append(f"supported=false but has {len(citations)} citation(s)")

    # Rule 4: numeric grounding — every number in the answer must appear in cited text
    cited_text = " ".join(chunk_text_by_id.get(cid, "") for cid in citations)
    if cited_text:
        for num in extract_numbers(answer_text):
            if num not in cited_text:
                issues.append(f"Numeric claim '{num}' not found in cited chunks")

    results.append(
        {
            "id": answer["id"],
            "passed": len(issues) == 0,
            "issues": issues,
        }
    )

with open("artifacts/citation_validation.json", "w") as f:
    json.dump(results, f, indent=2)

passed = sum(1 for r in results if r["passed"])
print(f"Validation complete: {passed}/{len(results)} passed → artifacts/citation_validation.json")
for r in results:
    if not r["passed"]:
        print(f"  FAIL [{r['id'][:8]}...]: {r['issues']}")
