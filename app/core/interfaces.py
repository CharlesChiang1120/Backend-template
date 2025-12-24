from abc import ABC, abstractmethod
from typing import Any, Dict, List

class BaseRepository(ABC):
    """
    Abstract Base Class for Data Persistence.
    Standardizes how every factory interacts with their local database.
    """
    @abstractmethod
    def get_one(self, id: Any) -> Dict[str, Any]:
        pass

    @abstractmethod
    def save(self, entity: Any) -> Any:
        pass

class GenAIServiceInterface(ABC):
    """
    Abstract Base Class for AI Operations.
    Decouples business logic from specific AI models (GPT-4 vs Llama-3).
    """
    @abstractmethod
    async def ask(self, prompt: str, system_message: str = "") -> str:
        """Standard method to get a text completion from AI."""
        pass

    @abstractmethod
    def get_token_usage(self) -> int:
        """Mandatory tracking for cost control in large enterprises."""
        pass