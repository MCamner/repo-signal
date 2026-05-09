from repo_signal.ai.providers.base import ProviderConfigurationError


class AnthropicProvider:
    def __init__(self, *args, **kwargs):
        raise ProviderConfigurationError(
            "Anthropic provider is a reserved adapter slot and is not implemented yet."
        )

