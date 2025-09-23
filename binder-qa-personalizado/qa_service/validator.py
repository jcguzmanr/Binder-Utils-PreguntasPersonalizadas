from typing import Dict, Any, List, Optional
from urllib.parse import urlparse


class QAValidator:
    """Validador para entrada de QA personalizado"""
    
    def __init__(self, config):
        self.config = config
    
    def validate_request(self, body: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida la entrada del request de QA.
        
        Returns:
            Dict con resultado de validación:
            - {"valid": True} si es válido
            - {"valid": False, "error": {"codigo": "...", "detalle": "..."}} si hay error
        """
        try:
            # Validar estructura básica
            if not isinstance(body, dict):
                return self._error("BAD_REQUEST", "Request body must be a JSON object")
            
            # Validar campos requeridos
            if "texto_contrato" not in body:
                return self._error("BAD_REQUEST", "Missing required field: texto_contrato")
            
            if "reference_id" not in body:
                return self._error("BAD_REQUEST", "Missing required field: reference_id")
            
            if "qa" not in body:
                return self._error("BAD_REQUEST", "Missing required field: qa")
            
            # Validar texto_contrato
            texto_contrato = body.get("texto_contrato")
            if not isinstance(texto_contrato, str) or len(texto_contrato.strip()) < self.config.min_chars_contrato:
                return self._error("BAD_REQUEST", f"texto_contrato must be a string with at least {self.config.min_chars_contrato} characters")
            
            # Validar reference_id
            reference_id = body.get("reference_id")
            if not isinstance(reference_id, str) or len(reference_id.strip()) == 0:
                return self._error("BAD_REQUEST", "reference_id must be a non-empty string")
            
            # Validar sección qa
            qa_section = body.get("qa")
            if not isinstance(qa_section, dict):
                return self._error("BAD_REQUEST", "qa section must be an object")
            
            # Validar preguntas
            preguntas = qa_section.get("preguntas")
            if not isinstance(preguntas, list):
                return self._error("BAD_REQUEST", "preguntas must be an array")
            
            if len(preguntas) == 0:
                return self._error("BAD_REQUEST", "preguntas array cannot be empty")
            
            if len(preguntas) > self.config.max_preguntas:
                return self._error("BAD_REQUEST", f"Maximum {self.config.max_preguntas} preguntas allowed")
            
            # Validar cada pregunta
            for i, pregunta in enumerate(preguntas):
                if not isinstance(pregunta, str):
                    return self._error("BAD_REQUEST", f"pregunta {i+1} must be a string")
                
                if len(pregunta.strip()) == 0:
                    return self._error("BAD_REQUEST", f"pregunta {i+1} cannot be empty")
                
                if len(pregunta) > self.config.max_chars_pregunta:
                    return self._error("BAD_REQUEST", f"pregunta {i+1} exceeds maximum length of {self.config.max_chars_pregunta} characters")
            
            # Validar webhook_url si está presente
            webhook_url = qa_section.get("webhook_url")
            if webhook_url is not None:
                if not isinstance(webhook_url, str):
                    return self._error("BAD_REQUEST", "webhook_url must be a string")
                
                webhook_valid, webhook_error = self._validate_webhook_url(webhook_url)
                if not webhook_valid:
                    return self._error("BAD_REQUEST", f"Invalid webhook_url: {webhook_error}")
            
            # Validar incluir_razonamiento si está presente
            incluir_razonamiento = qa_section.get("incluir_razonamiento")
            if incluir_razonamiento is not None and not isinstance(incluir_razonamiento, bool):
                return self._error("BAD_REQUEST", "incluir_razonamiento must be a boolean")
            
            return {"valid": True}
            
        except Exception as e:
            return self._error("BAD_REQUEST", f"Validation error: {str(e)}")
    
    def _validate_webhook_url(self, url: str) -> tuple[bool, Optional[str]]:
        """Valida URL de webhook"""
        try:
            parsed = urlparse(url)
            
            # Verificar esquema
            if parsed.scheme not in ("http", "https"):
                return False, "URL must use http or https scheme"
            
            # Verificar HTTPS si está requerido
            if self.config.require_https_webhook and parsed.scheme != "https":
                return False, "URL must use HTTPS"
            
            # Verificar dominio si hay restricciones
            if self.config.allowed_webhook_domains:
                hostname = parsed.hostname
                if not hostname:
                    return False, "Invalid hostname"
                
                hostname_lower = hostname.lower()
                allowed = False
                for allowed_domain in self.config.allowed_webhook_domains:
                    if hostname_lower == allowed_domain.lower() or hostname_lower.endswith("." + allowed_domain.lower()):
                        allowed = True
                        break
                
                if not allowed:
                    return False, f"Domain {hostname} not in allowed list"
            
            return True, None
            
        except Exception as e:
            return False, f"Invalid URL format: {str(e)}"
    
    def _error(self, codigo: str, detalle: str) -> Dict[str, Any]:
        """Crea respuesta de error"""
        return {
            "valid": False,
            "error": {
                "codigo": codigo,
                "detalle": detalle
            }
        }
