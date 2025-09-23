from dataclasses import dataclass
from typing import Tuple
import os


@dataclass(frozen=True)
class QAConfig:
    """Configuración específica para el servicio de QA personalizado"""
    
    # Límites de validación
    max_preguntas: int = int(os.environ.get("QA_MAX_PREGUNTAS", "50"))
    max_chars_pregunta: int = int(os.environ.get("QA_MAX_CHARS_PREGUNTA", "300"))
    min_chars_contrato: int = int(os.environ.get("QA_MIN_CHARS_CONTRATO", "100"))
    
    # Timeouts
    openai_timeout: int = int(os.environ.get("OPENAI_TIMEOUT", "60"))
    webhook_timeout: int = int(os.environ.get("WEBHOOK_TIMEOUT", "30"))
    max_total_timeout: int = int(os.environ.get("MAX_TOTAL_TIMEOUT", "120"))
    
    # OpenAI
    default_model: str = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    fallback_model: str = os.environ.get("OPENAI_FALLBACK_MODEL", "gpt-3.5-turbo")
    max_output_tokens: int = int(os.environ.get("OPENAI_MAX_OUTPUT_TOKENS", "4096"))
    
    # Webhook
    webhook_retry_attempts: int = int(os.environ.get("WEBHOOK_RETRY_ATTEMPTS", "3"))
    webhook_backoff_base: float = float(os.environ.get("WEBHOOK_BACKOFF_BASE", "1.5"))
    webhook_async_mode: bool = os.environ.get("WEBHOOK_ASYNC_MODE", "false").lower() == "true"
    
    # AWS
    region: str = os.environ.get("AWS_REGION", "us-east-1")
    log_level: str = os.environ.get("LOG_LEVEL", "INFO")
    
    # CORS
    allowed_origin: str = os.environ.get("ALLOWED_ORIGIN", "*")
    
    # Seguridad (opcional)
    require_https_webhook: bool = os.environ.get("REQUIRE_HTTPS_WEBHOOK", "false").lower() == "true"
    allowed_webhook_domains: Tuple[str, ...] = tuple(
        domain.strip() for domain in os.environ.get("ALLOWED_WEBHOOK_DOMAINS", "").split(",")
        if domain.strip()
    )


def default_config() -> QAConfig:
    """Retorna configuración por defecto"""
    return QAConfig()
