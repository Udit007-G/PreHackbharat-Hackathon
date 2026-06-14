import argparse
from pathlib import Path

from hindsight_memory import create_memory_client
from recommendation_engine import generate_recommendation
from reviewer import review_code


def format_review(path: Path, use_hindsight: bool = False) -> str:
    code = path.read_text(encoding="utf-8")
    findings = review_code(code)

    if not findings:
        return f"No findings in {path}."

    client = create_memory_client(use_hindsight=use_hindsight)
    sections = []

    try:
        for finding in findings:
            memories = client.recall(finding.message)
            recommendation = generate_recommendation(finding, memories)

            recalled = "\n".join(f"- {memory.text.strip()}" for memory in memories[:3])
            if not recalled:
                recalled = "- No relevant memories found."

            sections.append(
                "\n".join(
                    [
                        "=" * 60,
                        f"{path}:{finding.line}",
                        f"Rule: {finding.rule_id}",
                        f"Issue: {finding.message}",
                        f"Evidence: {finding.evidence}",
                        "",
                        "Relevant memories:",
                        recalled,
                        "",
                        "Recommendation:",
                        recommendation,
                    ]
                )
            )
    finally:
        client.close()

    return "\n\n".join(sections)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Review Python code with memory-aware recommendations."
    )
    parser.add_argument(
        "path",
        nargs="?",
        default="sample_code.py",
        help="Python file to review. Defaults to sample_code.py.",
    )
    parser.add_argument(
        "--use-hindsight",
        action="store_true",
        help="Use Hindsight instead of the local memory_seed.json file.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    print(format_review(Path(args.path), use_hindsight=args.use_hindsight))


if __name__ == "__main__":
    main()
