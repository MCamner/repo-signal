from pathlib import Path
import sys


CHECKS = [
    ("README.md", "README exists"),
    ("LICENSE", "License exists"),
    (".gitignore", ".gitignore exists"),
    ("docs", "docs folder exists"),
]


def exists(path: Path, target: str) -> bool:
    return (path / target).exists()


def scan_repo(repo: Path) -> str:
    lines = []
    lines.append("# Repo Signal Report")
    lines.append("")
    lines.append(f"Repo: `{repo.name}`")
    lines.append("")

    lines.append("## Checks")
    lines.append("")

    for target, label in CHECKS:
        status = "OK" if exists(repo, target) else "MISSING"
        lines.append(f"- [{status}] {label}: `{target}`")

    ds_store = list(repo.rglob(".DS_Store"))
    lines.append("")
    lines.append("## Hygiene")
    lines.append("")

    if ds_store:
        lines.append(f"- [WARN] Found `.DS_Store` files: {len(ds_store)}")
        for item in ds_store[:10]:
            lines.append(f"  - `{item.relative_to(repo)}`")
    else:
        lines.append("- [OK] No `.DS_Store` files found")

    lines.append("")
    lines.append("## Suggested next actions")
    lines.append("")
    lines.append("1. Improve README clarity")
    lines.append("2. Add or verify GitHub Pages docs")
    lines.append("3. Remove tracked system files")
    lines.append("4. Add project screenshots")
    lines.append("5. Create or update Wiki pages")

    return "\n".join(lines)


def main() -> None:
    command = sys.argv[1] if len(sys.argv) > 1 else "scan"

    if command != "scan":
        print(f"Unknown command: {command}")
        print("Available commands: scan")
        raise SystemExit(1)

    repo = Path.cwd()
    print(scan_repo(repo))


if __name__ == "__main__":
    main()
