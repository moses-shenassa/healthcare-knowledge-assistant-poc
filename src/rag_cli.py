from pathlib import Path

from openai import OpenAI

from .vector_store import load_vector_store, get_embedding

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore[no-redef]


def load_config(path: str = "config.toml"):
    with open(path, "rb") as f:
        return tomllib.load(f)


def load_prompt(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def main():
    cfg = load_config()
    client = OpenAI(api_key=cfg["openai"]["api_key"])
    vs = load_vector_store()

    system_prompt = load_prompt("prompts/system_prompt.md")
    safety_prompt = load_prompt("prompts/safety_guidelines.md")

    print("Healthcare Knowledge Assistant PoC")
    print("Type 'exit' to quit.\n")

    while True:
        q = input("> ").strip()
        if q.lower() in {"exit", "quit"}:
            break
        if not q:
            continue

        emb = get_embedding(client, q)
        hits = vs.search(emb, k=5)
        context_blocks = [t for _, t in hits]
        context = "\n\n".join(context_blocks)

        messages = [
            {
                "role": "system",
                "content": system_prompt + "\n\n" + safety_prompt,
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {q}",
            },
        ]

        resp = client.chat.completions.create(
            model=cfg["openai"]["model"],
            messages=messages,
        )
        answer = resp.choices[0].message.content
        print("\n" + answer + "\n" + "-" * 60)


if __name__ == "__main__":
    main()
