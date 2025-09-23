import json
import time
import socket
from typing import Dict, Any, Optional, Tuple
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from urllib.parse import urlparse
import ssl


class WebhookService:
    """Servicio para envío de webhooks con reintentos"""
    
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
    
    def _validate_webhook_url(self, webhook_url: str) -> Tuple[bool, Optional[str]]:
        """Valida la URL del webhook"""
        try:
            parsed = urlparse(webhook_url)
            
            # Verificar esquema
            if parsed.scheme not in ['http', 'https']:
                return False, f"Invalid scheme: {parsed.scheme}. Only HTTP/HTTPS allowed."
            
            # Verificar que tenga host
            if not parsed.netloc:
                return False, "Missing host in URL"
            
            # Verificar HTTPS si está configurado
            if self.config.require_https_webhook and parsed.scheme != 'https':
                return False, "HTTPS required for webhook URLs"
            
            # Verificar dominios permitidos si están configurados
            if self.config.allowed_webhook_domains:
                domain = parsed.netloc.lower()
                if not any(domain.endswith(allowed.lower()) for allowed in self.config.allowed_webhook_domains):
                    return False, f"Domain {domain} not in allowed list: {self.config.allowed_webhook_domains}"
            
            return True, None
            
        except Exception as e:
            return False, f"URL validation error: {str(e)}"
    
    def send_webhook(self, webhook_url: str, payload: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Envía webhook con reintentos exponenciales.
        
        Args:
            webhook_url: URL del webhook
            payload: Datos a enviar
            
        Returns:
            Tuple con (success, error_message)
        """
        # Validar URL primero
        is_valid, validation_error = self._validate_webhook_url(webhook_url)
        if not is_valid:
            self.logger.event("webhook.validation_failed", url=webhook_url, error=validation_error)
            return False, validation_error
        
        attempts = self.config.webhook_retry_attempts
        backoff_base = self.config.webhook_backoff_base
        
        last_error = None
        
        for attempt in range(attempts):
            if attempt > 0:
                # Backoff exponencial
                delay = backoff_base ** attempt
                self.logger.event("webhook.retry", attempt=attempt+1, delay=delay)
                time.sleep(delay)
            
            try:
                success, error = self._send_single_webhook(webhook_url, payload)
                
                if success:
                    self.logger.event("webhook.success", attempt=attempt+1)
                    return True, None
                else:
                    last_error = error
                    self.logger.event("webhook.failed", attempt=attempt+1, error=error)
                    
            except Exception as e:
                last_error = str(e)
                self.logger.event("webhook.exception", attempt=attempt+1, error=str(e))
        
        self.logger.event("webhook.gave_up", attempts=attempts, final_error=last_error)
        return False, last_error
    
    def _send_single_webhook(self, webhook_url: str, payload: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Envía un solo webhook"""
        try:
            # Log detallado del intento
            self.logger.event("webhook.attempt", 
                            url=webhook_url, 
                            timeout=self.config.webhook_timeout,
                            payload_size=len(json.dumps(payload)))
            
            # Preparar datos
            data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            
            # Crear request
            req = Request(
                webhook_url,
                data=data,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "Binder-QA-Service/1.0"
                },
                method="POST"
            )
            
            # Configurar SSL
            ctx = ssl.create_default_context()
            
            # Enviar request
            with urlopen(req, timeout=self.config.webhook_timeout, context=ctx) as response:
                status_code = response.getcode()
                
                # Log respuesta
                self.logger.event("webhook.response", 
                                status_code=status_code,
                                headers=dict(response.headers))
                
                if 200 <= status_code < 300:
                    return True, None
                else:
                    return False, f"HTTP {status_code}"
                    
        except HTTPError as e:
            try:
                error_body = e.read().decode("utf-8", errors="replace")
                self.logger.event("webhook.http_error", 
                                code=e.code, 
                                reason=e.reason,
                                body=error_body[:500])  # Limitar tamaño del log
            except Exception:
                error_body = ""
                self.logger.event("webhook.http_error", 
                                code=e.code, 
                                reason=e.reason,
                                body="Could not read error body")
            
            return False, f"HTTP {e.code}: {error_body}"
            
        except socket.timeout:
            self.logger.event("webhook.timeout", timeout=self.config.webhook_timeout)
            return False, "Request timeout"
            
        except Exception as e:
            self.logger.event("webhook.exception", error=str(e), error_type=type(e).__name__)
            return False, str(e)
    
    def send_webhook_async(self, webhook_url: str, payload: Dict[str, Any]) -> None:
        """
        Envía webhook de forma asíncrona (fire-and-forget).
        
        Para uso en Lambda donde no podemos esperar el resultado.
        """
        try:
            # En Lambda, solo logueamos la intención
            self.logger.event("webhook.async_send", url=webhook_url, payload_keys=list(payload.keys()))
            
            # En un entorno real, aquí podrías usar SQS, SNS, o invocar otra Lambda
            # Para simplicidad, intentamos enviar directamente
            success, error = self.send_webhook(webhook_url, payload)
            
            if success:
                self.logger.event("webhook.async_success")
            else:
                self.logger.event("webhook.async_failed", error=error)
                
        except Exception as e:
            self.logger.event("webhook.async_exception", error=str(e))
