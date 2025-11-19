"""Simple CLI interface for interacting with the Healthcare RAG PoC."""

import argparse
import textwrap

from config import load_config
from rag import HealthcareRAG


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Healthcare Knowledge Assistant — RAG PoC CLI"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config.toml",
        help="Path to config.toml",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Show retrieved contexts for each answer.",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    rag = HealthcareRAG(config)

    print("Healthcare Knowledge Assistant — RAG PoC")
    print("Type your question and press Enter. Type 'exit' or 'quit' to leave.\n")

    while True:
        try:
            question = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if question.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break

        if not question:
            continue

        result = rag.answer(question, debug=args.debug)
        print("\n" + textwrap.fill(result["answer"], width=88) + "\n")

        if args.debug and "contexts" in result:
            print("Retrieved context chunks:")
            for c in result["contexts"]:
                print(
                    f"- {c['source']} (chunk {c['chunk_id']}, score={c['score']:.4f})"
                )
            print()


if __name__ == "__main__":
    main()
