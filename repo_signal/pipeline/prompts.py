from typing import Dict, List


BASE_PROMPT = """You are repo-signal, an AI-native repository intelligence assistant.

Answer questions about this repository using only the provided context when possible.
Prefer concrete file references. Be explicit about uncertainty when the context is incomplete.
Do not invent files, commands, or behavior that are not supported by the context.

Return the answer with these sections:
- Summary
- Referenced files
- Architecture notes
- Answer
"""

DEBUG_PROMPT = """You are debugging a repository issue.

Focus on:
- routing and control flow
- error paths and likely failure points
- modified files when they are relevant
- concrete next inspection steps
"""

ARCHITECT_PROMPT = """You are reviewing repository architecture.

Focus on:
- structure and boundaries
- modularity and coupling
- extensibility
- roadmap implications
"""

EXPLAIN_PROMPT = """You are explaining repository behavior.

Focus on:
- the shortest accurate walkthrough
- the highest-signal files first
- concrete names from the code
- practical caveats when context is incomplete
"""

REVIEW_PROMPT = """You are reviewing repository changes and risks.

Focus on:
- correctness risks
- maintainability smells
- shell and CLI pitfalls
- missing tests or unclear behavior
"""

MODE_PROMPTS: Dict[str, str] = {
    "architect": ARCHITECT_PROMPT,
    "debug": DEBUG_PROMPT,
    "explain": EXPLAIN_PROMPT,
    "review": REVIEW_PROMPT,
}


def prompt_for_mode(mode: str) -> str:
    try:
        return MODE_PROMPTS[mode]
    except KeyError as exc:
        raise ValueError(f"Unknown ask mode: {mode}") from exc


def build_ask_prompt(
    question: str,
    context: str,
    mode: str,
    referenced_files: List[str],
) -> str:
    files = "\n".join(f"- {path}" for path in referenced_files) or "- No ranked files found."
    mode_prompt = prompt_for_mode(mode)

    return f"""{BASE_PROMPT}

{mode_prompt}

<question>
{question}
</question>

<selected_files>
{files}
</selected_files>

<repo_context>
{context}
</repo_context>
"""

