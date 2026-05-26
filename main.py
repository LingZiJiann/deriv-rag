import json
import subprocess
import sys

STEPS = [
    ("Chunking documents",    "chunk.py"),
    ("Generating embeddings", "embed.py"),
    ("Generating answers",    "generate.py"),
    ("Validating citations",  "validate.py"),
    ("Merging final output",  "merge.py"),
]


def run_step(label: str, script: str) -> None:
    print(f"\n[{label}]")
    result = subprocess.run([sys.executable, script])
    if result.returncode != 0:
        raise SystemExit(f"Pipeline failed at: {script}")


def main() -> None:
    for label, script in STEPS:
        run_step(label, script)

    documents  = json.load(open("artifacts/documents.json"))
    chunks     = json.load(open("artifacts/chunks.json"))
    questions  = json.load(open("questions.json"))
    answers    = json.load(open("artifacts/answers.json"))
    validation = json.load(open("artifacts/citation_validation.json"))

    supported = sum(1 for a in answers if a["supported"])
    failures  = sum(1 for v in validation if not v["passed"])

    print("\n" + "=" * 40)
    print("Pipeline Summary")
    print("=" * 40)
    print(f"  Documents:           {len(documents)}")
    print(f"  Chunks:              {len(chunks)}")
    print(f"  Questions:           {len(questions)}")
    print(f"  Supported answers:   {supported}/{len(answers)}")
    print(f"  Validation failures: {failures}")
    print("=" * 40)


if __name__ == "__main__":
    main()
