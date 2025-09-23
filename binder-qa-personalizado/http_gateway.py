from typing import Any, Dict, Tuple, Optional
import json
import base64


_HTTP_HINT_KEYS = (
    "body",
    "requestContext",
    "rawPath",
    "resource",
    "httpMethod",
    "version",
)


def parse_body(event: Any) -> Tuple[Dict[str, Any], bool]:
    """
    Parsea el cuerpo del evento Lambda.
    
    Soporta API Gateway (REST/HTTP) e invocación directa, incluyendo cuerpos
    codificados en base64 (isBase64Encoded=true).
    
    Returns:
        Tuple con (body_parsed, is_http_request)
    """
    if isinstance(event, str):
        return json.loads(event), False
    
    if isinstance(event, dict):
        if "body" in event:
            body = event.get("body")
            if isinstance(body, str) and event.get("isBase64Encoded"):
                try:
                    body = base64.b64decode(body).decode("utf-8")
                except Exception:
                    # Si no se puede decodificar, devolvemos cuerpo vacío
                    body = "{}"
            return (json.loads(body) if isinstance(body, str) else (body or {})), True
        
        return (event or {}), any(k in event for k in _HTTP_HINT_KEYS)
    
    return {}, False


class Responder:
    """Unifica respuestas HTTP/directas con headers opcionales + CORS"""
    
    def __init__(self, is_http: bool, cors_origin: str = "*"):
        self.is_http = is_http
        self.cors_origin = cors_origin
    
    def _base_headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": self.cors_origin,
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Access-Control-Allow-Methods": "OPTIONS,POST",
            "Access-Control-Max-Age": "600",
            "Access-Control-Expose-Headers": "Retry-After",
            "Vary": "Origin",
        }
    
    def preflight(self) -> Dict[str, Any]:
        """Respuesta para preflight CORS requests"""
        if not self.is_http:
            return {"ok": True}
        
        return {
            "statusCode": 204,
            "headers": self._base_headers(),
            "isBase64Encoded": False,
            "body": "",
        }
    
    def respond(
        self,
        status: int,
        body: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Genera respuesta HTTP o directa según el contexto"""
        if self.is_http:
            hdrs = self._base_headers()
            if headers:
                hdrs.update(headers)
            
            return {
                "statusCode": status,
                "headers": hdrs,
                "isBase64Encoded": False,
                "body": json.dumps(body, ensure_ascii=False),
            }
        
        # Respuesta directa (no HTTP)
        if status < 400:
            return body
        else:
            return {"ok": False, "status": status, **body}
