from dependency_injector import containers, providers
from app.core.config import settings
from app.adapters.ai_provider import OpenAIAdapter

class Container(containers.DeclarativeContainer):
    """
    The Dependency Injection Container.
    This manages the lifecycle of all services and ensures loose coupling.
    """
    
    # 1. Configuration provider: Injects settings from app/core/config.py
    config = providers.Configuration()
    config.from_dict(settings.model_dump())

    # 2. AI Service provider:
    # Here, we tell the system: whenever someone needs an AI service, 
    # use the OpenAIAdapter and give it the API Key from our settings.
    ai_service = providers.Singleton(
        OpenAIAdapter,
        api_key=settings.OPENAI_API_KEY
    )

    # Note for the future:
    # If a factory uses a different DB, you'd define it here similarly.
    # db_service = providers.Singleton(PostgresRepository, url=settings.DATABASE_URL)