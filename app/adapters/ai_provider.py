from openai import AsyncOpenAI
from app.core.interfaces import GenAIServiceInterface
from app.core.logger import logger
import structlog

# Initialize structured logger for this module
log = structlog.get_logger()

class OpenAIAdapter(GenAIServiceInterface):
    """
    OpenAI Implementation of the GenAIServiceInterface.
    This adapter encapsulates all OpenAI-specific logic, allowing the rest 
    of the system to remain agnostic of the underlying AI provider.
    """

    def __init__(self, api_key: str, model_name: str = "gpt-4o"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model_name = model_name
        self.token_usage = 0

    async def ask(self, prompt: str) -> str:
        """
        Sends a prompt to OpenAI and returns the content string.
        Includes robust error handling and structured logging for audit trails.
        """
        try:
            log.info("ai_request_sent", provider="openai", model=self.model_name)
            
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )

            # Update token usage metrics
            usage = response.usage.total_tokens
            self.token_usage += usage
            
            content = response.choices[0].message.content
            
            log.info("ai_response_received", tokens=usage, status="success")
            return content

        except Exception as e:
            # Centralized error logging for global factory monitoring
            log.error("ai_provider_error", error=str(e), provider="openai")
            return f"Error: AI service is currently unavailable. (Trace: {str(e)})"

    def get_token_usage(self) -> int:
        """Returns the cumulative token usage for this instance."""
        return self.token_usage