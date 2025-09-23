from dataclasses import dataclass
from typing import Optional, Tuple, Dict, Any, List
import os
import json

from .http import HTTPClient
from .qa_parser import qa_parser
from .prompt import format_qa_prompt


@dataclass
class OpenAIConfig:
    """Configuración para OpenAI API"""
    model: str = "gpt-4o-mini"
    timeout: int = 60
    max_output_tokens: int = 4096
    fallback_model: str = "gpt-3.5-turbo"
    log: Any = None


class OpenAIService:
    """Servicio para interactuar con OpenAI API para QA"""
    
    CHAT_URL = "https://api.openai.com/v1/chat/completions"
    
    def __init__(self, http: HTTPClient, cfg: OpenAIConfig):
        self.http = http
        self.cfg = cfg
    
    def _log(self, event: str, **kw):
        """Log con contexto"""
        if self.cfg.log:
            try:
                self.cfg.log.event(event, **kw)
            except Exception:
                pass
    
    def _trim_text(self, text: str, max_chars: int = 100000) -> Tuple[str, bool]:
        """Recorta texto si es muy largo"""
        if not text:
            return "", False
        return (text, False) if len(text) <= max_chars else (text[:max_chars], True)
    
    def _build_chat_body(self, prompt: str, model: Optional[str] = None) -> Dict[str, Any]:
        """Construye el body para chat completions"""
        return {
            "model": model or self.cfg.model,
            "messages": [
                {"role": "system", "content": "Eres un experto en análisis de contratos. Responde ÚNICAMENTE con JSON válido."},
                {"role": "user", "content": prompt},
            ],
            "max_completion_tokens": self.cfg.max_output_tokens,
            "response_format": {"type": "json_object"},
            "temperature": 0.1,  # Baja temperatura para respuestas consistentes
        }
    
    def _call_chat(self, prompt: str, model: Optional[str] = None) -> Tuple[Optional[int], Optional[str], Optional[str]]:
        """Llama a OpenAI Chat API"""
        body = self._build_chat_body(prompt, model)
        return self.http.post(self.CHAT_URL, body)
    
    def run_qa(self, texto_contrato: str, preguntas: List[str], 
               incluir_razonamiento: bool = False) -> Tuple[Optional[List[Dict[str, Any]]], Optional[str]]:
        """
        Ejecuta QA sobre un contrato con múltiples preguntas.
        
        Args:
            texto_contrato: Texto del contrato
            preguntas: Lista de preguntas
            incluir_razonamiento: Si incluir razonamiento en respuestas
            
        Returns:
            Tuple con (respuestas_normalizadas, error_message)
        """
        try:
            # Formatear prompt
            prompt = format_qa_prompt(texto_contrato, preguntas, incluir_razonamiento)
            
            # Recortar texto si es muy largo
            safe_text, was_trimmed = self._trim_text(prompt, max_chars=120000)
            if was_trimmed:
                self._log("ai.text_trimmed", original_len=len(prompt), trimmed_len=len(safe_text))
            
            # Intentar con modelo principal
            self._log("ai.qa_start", model=self.cfg.model, questions_count=len(preguntas))
            
            status, raw_response, error = self._call_chat(safe_text)
            
            if status and 200 <= status < 300 and raw_response:
                # Parsear respuesta
                parsed_data, parse_error = qa_parser.parse_any(raw_response)
                
                if parsed_data is not None:
                    # Normalizar respuestas
                    normalized = qa_parser.normalize_qa_responses(
                        parsed_data, preguntas, incluir_razonamiento
                    )
                    
                    self._log("ai.qa_success", model=self.cfg.model, responses_count=len(normalized))
                    return normalized, None
                else:
                    self._log("ai.parse_error", err=parse_error or "Unknown parse error")
            
            # Si falló, intentar con modelo de fallback
            if self.cfg.fallback_model and self.cfg.fallback_model != self.cfg.model:
                self._log("ai.fallback_attempt", fallback_model=self.cfg.fallback_model)
                
                status2, raw_response2, error2 = self._call_chat(safe_text, self.cfg.fallback_model)
                
                if status2 and 200 <= status2 < 300 and raw_response2:
                    parsed_data2, parse_error2 = qa_parser.parse_any(raw_response2)
                    
                    if parsed_data2 is not None:
                        normalized2 = qa_parser.normalize_qa_responses(
                            parsed_data2, preguntas, incluir_razonamiento
                        )
                        
                        self._log("ai.fallback_success", model=self.cfg.fallback_model, responses_count=len(normalized2))
                        return normalized2, None
                    else:
                        self._log("ai.fallback_parse_error", err=parse_error2 or "Unknown parse error")
            
            # Si todo falló, retornar error
            error_msg = error or "Unknown API error"
            self._log("ai.qa_failed", err=error_msg, status=status or 0)
            return None, f"OpenAI API error: {error_msg}"
            
        except Exception as e:
            self._log("ai.qa_exception", err=str(e), error_type=type(e).__name__)
            import traceback
            self._log("ai.qa_exception_trace", traceback=traceback.format_exc())
            return None, f"Exception: {str(e)}"
