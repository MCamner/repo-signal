import os
import subprocess

from repo_signal.ai.providers.base import ProviderConfigurationError


DEFAULT_MODEL = "gpt-5.5"
DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"


def load_dotenv_if_available() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return

    load_dotenv()


def load_shell_openai_key_if_available() -> None:
    if os.getenv("OPENAI_API_KEY"):
        return

    try:
        result = subprocess.run(
            ["zsh", "-lc", "print -r -- ${OPENAI_API_KEY:-}"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    except Exception:
        return

    value = result.stdout.strip()
    if value:
        os.environ["OPENAI_API_KEY"] = value


class OpenAIProvider:
    def __init__(self, model: str = DEFAULT_MODEL, embedding_model: str = DEFAULT_EMBEDDING_MODEL):
        load_dotenv_if_available()
        load_shell_openai_key_if_available()

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ProviderConfigurationError(
                "OPENAI_API_KEY is not available in this process. "
                "Export it in your shell before running repo-signal ask."
            )

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ProviderConfigurationError(
                "The OpenAI Python package is not installed. Install the optional AI dependencies first."
            ) from exc

        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.embedding_model = embedding_model

    def generate(self, prompt: str) -> str:
        response = self.client.responses.create(
            model=self.model,
            input=prompt,
        )
        return response.output_text

    def embed(self, text: str) -> list[float]:
        response = self.client.embeddings.create(
            model=self.embedding_model,
            input=text,
        )
        return response.data[0].embedding
