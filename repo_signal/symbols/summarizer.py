from repo_signal.core.models import Symbol


ACTION_WORDS = {
    "analyze": "analyzes",
    "ask": "orchestrates AI-backed repository questions",
    "build": "builds",
    "detect": "detects",
    "extract": "extracts",
    "format": "formats",
    "generate": "generates",
    "rank": "ranks",
    "read": "reads",
    "run": "runs",
    "scan": "scans",
    "score": "scores",
    "summarize": "summarizes",
    "write": "writes",
}


def humanize_name(name: str) -> str:
    return name.replace("_", " ").replace("-", " ").strip()


def summarize_symbol(symbol: Symbol) -> str:
    words = humanize_name(symbol.name).split()
    if not words:
        return f"{symbol.name}: {symbol.kind} in {symbol.file_path}."

    verb = ACTION_WORDS.get(words[0].lower())
    subject = " ".join(words[1:]) if len(words) > 1 else humanize_name(symbol.name)

    if verb:
        description = f"{verb} {subject}".strip()
    elif symbol.kind == "class":
        description = f"groups behavior for {humanize_name(symbol.name)}"
    elif symbol.kind == "shell_function":
        description = f"shell workflow for {humanize_name(symbol.name)}"
    elif symbol.kind == "powershell_function":
        description = f"PowerShell workflow for {humanize_name(symbol.name)}"
    else:
        description = f"implements {humanize_name(symbol.name)}"

    return f"{symbol.name}: {description} in {symbol.file_path}."

