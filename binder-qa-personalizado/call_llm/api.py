from typing import Optional, Tuple, List, Dict, Any
import os

from .env import load_env_openai_key
from .http import HTTPClient
from .openai_service import OpenAIConfig, OpenAIService


def generate_qa_responses(
    *,
    texto_contrato: str,
    preguntas: List[str],
    incluir_razonamiento: bool = False,
    model: str = "gpt-4o-mini",
    timeout: int = 60,
    log=None,
) -> Tuple[Optional[List[Dict[str, Any]]], Optional[str]]:
    """
    Genera respuestas de QA para preguntas sobre un contrato.
    
    Args:
        texto_contrato: Texto del contrato a analizar
        preguntas: Lista de preguntas a responder
        incluir_razonamiento: Si incluir campo razonamiento
        model: Modelo de OpenAI a usar
        timeout: Timeout para la llamada
        log: Logger para eventos
        
    Returns:
        Tuple con (respuestas_normalizadas, error_message)
    """
    # Verificar API key
    api_key = load_env_openai_key()
    if not api_key:
        if log:
            log.event("ai.openai_key_missing")
        return None, "Missing OPENAI_API_KEY"
    
    # Configurar OpenAI
    cfg = OpenAIConfig(
        model=model,
        timeout=timeout,
        max_output_tokens=int(os.environ.get("OPENAI_MAX_OUTPUT_TOKENS", "4096")),
        fallback_model=os.environ.get("OPENAI_FALLBACK_MODEL", "gpt-3.5-turbo"),
        log=log,
    )
    
    # Crear cliente HTTP y servicio
    http = HTTPClient(api_key=api_key, timeout=cfg.timeout)
    service = OpenAIService(http, cfg)
    
    # Ejecutar QA
    return service.run_qa(
        texto_contrato=texto_contrato,
        preguntas=preguntas,
        incluir_razonamiento=incluir_razonamiento
    )
