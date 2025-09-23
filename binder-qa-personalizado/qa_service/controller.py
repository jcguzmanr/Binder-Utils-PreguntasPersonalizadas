from typing import Dict, Any, Optional, List
import time
from datetime import datetime, timezone

from .validator import QAValidator
from .webhook_service import WebhookService
from call_llm.api import generate_qa_responses
from config import QAConfig


class QAController:
    """Controller principal para el servicio de QA personalizado"""
    
    def __init__(self, config: QAConfig, logger):
        self.config = config
        self.logger = logger
        self.validator = QAValidator(config)
        self.webhook_service = WebhookService(config, logger)
    
    def handle_request(self, body: Dict[str, Any]) -> Dict[str, Any]:
        """
        Maneja un request de QA personalizado.
        
        Args:
            body: Cuerpo del request
            
        Returns:
            Respuesta estructurada con resultado o error
        """
        start_time = time.perf_counter()
        
        try:
            # Validar entrada
            validation_result = self.validator.validate_request(body)
            if not validation_result.get("valid", False):
                return self._create_error_response(
                    validation_result.get("error", {}).get("codigo", "BAD_REQUEST"),
                    validation_result.get("error", {}).get("detalle", "Validation failed"),
                    body.get("reference_id")
                )
            
            # Extraer datos validados
            texto_contrato = body.get("texto_contrato")
            reference_id = body.get("reference_id")
            qa_section = body.get("qa")
            preguntas = qa_section.get("preguntas")
            webhook_url = qa_section.get("webhook_url")
            incluir_razonamiento = qa_section.get("incluir_razonamiento", False)
            
            # Log inicio
            self.logger.event(
                "qa.start",
                id=reference_id,
                preguntas_count=len(preguntas),
                incluir_razonamiento=incluir_razonamiento,
                has_webhook=bool(webhook_url)
            )
            
            # Generar respuestas con OpenAI
            qa_resultados, error = generate_qa_responses(
                texto_contrato=texto_contrato,
                preguntas=preguntas,
                incluir_razonamiento=incluir_razonamiento,
                model=self.config.default_model,
                timeout=self.config.openai_timeout,
                log=self.logger
            )
            
            if qa_resultados is None:
                return self._create_error_response(
                    "MODEL_ERROR",
                    error or "Failed to generate responses",
                    reference_id
                )
            
            # Calcular tiempo transcurrido
            end_time = time.perf_counter()
            latencia_ms = int((end_time - start_time) * 1000)
            
            # Crear respuesta exitosa
            response = {
                "success": True,
                "reference_id": reference_id,
                "qa_resultados": qa_resultados,
                "metadatos": {
                    "modelo": self.config.default_model,
                    "latencia_ms": latencia_ms,
                    "modo": "sync",
                    "webhook_disparado": False
                }
            }
            
            # Enviar webhook si está configurado
            webhook_success = True
            if webhook_url:
                try:
                    if self.config.webhook_async_mode:
                        # Modo asíncrono: no esperamos respuesta
                        self.webhook_service.send_webhook_async(webhook_url, response)
                        response["metadatos"]["webhook_disparado"] = True
                        response["metadatos"]["modo"] = "async"
                        self.logger.event("webhook.async_dispatched", id=reference_id, url=webhook_url)
                    else:
                        # Modo síncrono: esperamos respuesta
                        webhook_success, webhook_error = self.webhook_service.send_webhook(webhook_url, response)
                        response["metadatos"]["webhook_disparado"] = webhook_success
                        
                        if not webhook_success:
                            self.logger.event("webhook.failed", id=reference_id, error=webhook_error)
                            # No fallar el request por webhook, solo loguear
                        
                except Exception as e:
                    self.logger.event("webhook.exception", id=reference_id, error=str(e))
                    response["metadatos"]["webhook_disparado"] = False
            
            # Log éxito
            self.logger.event(
                "qa.success",
                id=reference_id,
                respuestas_count=len(qa_resultados),
                latencia_ms=latencia_ms,
                webhook_success=webhook_success
            )
            
            return response
            
        except Exception as e:
            # Log error
            end_time = time.perf_counter()
            latencia_ms = int((end_time - start_time) * 1000)
            
            self.logger.event(
                "qa.error",
                id=body.get("reference_id"),
                error=str(e),
                latencia_ms=latencia_ms
            )
            
            return self._create_error_response(
                "MODEL_ERROR",
                f"Internal error: {str(e)}",
                body.get("reference_id")
            )
    
    def _create_error_response(self, codigo: str, detalle: str, reference_id: Optional[str] = None) -> Dict[str, Any]:
        """Crea respuesta de error estructurada"""
        return {
            "success": False,
            "reference_id": reference_id,
            "error": {
                "codigo": codigo,
                "detalle": detalle
            }
        }
    
    def _now_utc_iso(self) -> str:
        """Retorna timestamp UTC en formato ISO"""
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
