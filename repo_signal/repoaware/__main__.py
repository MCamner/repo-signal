import sys
from pathlib import Path

from repo_signal.repoaware.context_builder import build_context


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage:")
        print('  python -m repo_signal.repoaware "question"')
        raise SystemExit(1)

    question = " ".join(sys.argv[1:])
    context = build_context(
        repo_path=Path.cwd(),
        question=question,
    )

    print(context)


if __name__ == "__main__":
    main()

