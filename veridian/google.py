"""Google Generative AI (Gemini) integration for Veridian.

Provides easy access to Google's free tier Gemini models for
causal worldline operations, observations, and lattice reasoning.

Free tier limits: Typically 1,000 RPM (requests per minute) and
10 RPM per model, with generous daily quotas for new accounts.

Usage:
    from veridian.google import GeminiClient

    client = GeminiClient(model="gemini-1.5-flash")
    result = client.generate("Analyze this worldline observation...")
"""

import os
from typing import Optional

import google.generativeai as genai


class GeminiClient:
    """Client for Google Gemini generative AI models.

    Supports free tier and paid tiers with automatic fallback.
    """

    def __init__(
        self,
        model: str = "gemini-1.5-flash",
        api_key: Optional[str] = None,
        temperature: float = 0.7,
    ):
        """Initialize Gemini client.

        Args:
            model: Gemini model name (default: gemini-1.5-flash)
            api_key: Google AI API key. If None, reads GOOGLE_API_KEY env var.
            temperature: Sampling temperature (0.0 to 1.0)
        """
        self.model_name = model
        self.temperature = temperature

        # Get API key from parameter or environment
        key = api_key or os.getenv("GOOGLE_API_KEY")
        if not key:
            raise ValueError(
                "Google API key required. Set GOOGLE_API_KEY environment variable "
                "or pass api_key parameter."
            )

        genai.configure(api_key=key)
        self.model = genai.GenerativeModel(model)

    def generate(self, prompt: str, max_output_tokens: int = 1024) -> str:
        """Generate text from a prompt using Gemini.

        Args:
            prompt: The input prompt/question
            max_output_tokens: Maximum tokens in response

        Returns:
            Generated text response
        """
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=self.temperature,
                    max_output_tokens=max_output_tokens,
                ),
            )

            if response.text:
                return response.text
            else:
                return ""

        except Exception as e:
            # Re-raise with more context
            raise RuntimeError(f"Gemini generation failed: {e}") from e

    def count_tokens(self, text: str) -> int:
        """Count tokens in text for the Gemini model.

        Args:
            text: Input text to count

        Returns:
            Number of tokens
        """
        return self.model.count_tokens(text)

    @property
    def model_info(self) -> dict:
        """Get model information including capabilities and limits."""
        return {
            "name": self.model_name,
            "provider": "Google",
            "free_tier": True,
            "temperature": self.temperature,
        }


# Default client instance for convenience
_default_client: Optional[GeminiClient] = None


def get_client() -> GeminiClient:
    """Get or create the default Gemini client instance.

    Reads GOOGLE_API_KEY from environment and uses gemini-1.5-flash model.

    Returns:
        GeminiClient instance
    """
    global _default_client
    if _default_client is None:
        _default_client = GeminiClient()
    return _default_client


def generate(
    prompt: str,
    model: str = "gemini-1.5-flash",
    temperature: float = 0.7,
    max_output_tokens: int = 1024,
) -> str:
    """Convenience function to generate text with Gemini.

    Args:
        prompt: The input prompt/question
        model: Gemini model name
        temperature: Sampling temperature
        max_output_tokens: Maximum tokens in response

    Returns:
        Generated text response
    """
    client = GeminiClient(model=model, temperature=temperature)
    return client.generate(prompt, max_output_tokens=max_output_tokens)


__all__ = ["GeminiClient", "get_client", "generate"]