from typing import Protocol


class BaseProvider(Protocol):
    def generate(self, prompt: str) -> str:
        raise NotImplementedError

    def embed(self, text: str) -> list[float]:
        raise NotImplementedError


class ProviderConfigurationError(RuntimeError):
    """Raised when an AI provider is missing credentials or dependencies."""

