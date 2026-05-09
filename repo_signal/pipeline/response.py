from dataclasses import dataclass, field
from typing import List

from repo_signal.core.models import Repository, Signal


@dataclass
class AskPipelineResult:
    repo: Repository
    question: str
    mode: str
    context: str
    prompt: str
    signals: List[Signal] = field(default_factory=list)
    answer: str = ""

    @property
    def referenced_files(self) -> List[str]:
        return [signal.file_path for signal in self.signals]


def format_pipeline_output(result: AskPipelineResult, dry_run: bool = False) -> str:
    if dry_run:
        return result.prompt

    answer = result.answer.strip()
    if not result.referenced_files:
        return answer

    if "referenced file" in answer.lower() or "referenced files" in answer.lower():
        return answer

    files = "\n".join(f"- `{path}`" for path in result.referenced_files)
    return f"{answer}\n\nReferenced files:\n{files}"

