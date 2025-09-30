# lambda_function.py
# Handler de AWS Lambda para QA personalizado

LOG_LEVEL = "INFO"

# ===== Imports del servicio ===================================================
from qa_service.controller import QAController
from qa_service.validator import QAValidator
from http_gateway import parse_body, Responder
from config import default_config
from app_logging import get_app_logger
from aws_clients import make_boto_clients, is_aws_environment
from time import perf_counter

logger = get_app_logger(json_logs=True, level=LOG_LEVEL)
CONFIG = default_config()


def _get_http_method(event) -> str:
    """Extrae método HTTP del evento"""
    if not isinstance(event, dict):
        return ""
    if "httpMethod" in event:  # REST API
        return event["httpMethod"] or ""
    rc = event.get("requestContext") or {}
    http = rc.get("http") or {}  # HTTP API v2
    return http.get("method", "")


def _get_function_name_from_ctx(ctx) -> str:
    """Extrae nombre de función del contexto Lambda"""
    try:
        return getattr(ctx, "function_name") or ""
    except Exception:
        return ""


def _get_http_info(event) -> dict:
    """Extrae información HTTP del evento"""
    if not isinstance(event, dict):
        return {}
    method = (_get_http_method(event) or "").upper()
    path = event.get("rawPath") or event.get("path") or event.get("resource") or ""
    headers = event.get("headers") or {}
    origin = headers.get("origin") or headers.get("Origin") or ""
    return {"method": method, "path": path, "origin": origin}


# ===== Handler ===============================================================
def lambda_handler(event, context):
    """Handler principal de Lambda para QA personalizado"""
    start = perf_counter()
    
    # Parsear evento
    body, is_http = parse_body(event)
    reference_id = body.get("reference_id") if isinstance(body, dict) else None
    fn = _get_function_name_from_ctx(context)
    http = _get_http_info(event) if is_http else {}
    mode = "HTTP" if is_http else "DIRECT"
    
    # Log inicio
    logger.event(
        "🚀 qa.start",
        id=reference_id,
        fn=fn,
        mode=mode,
        **({"method": http.get("method"), "path": http.get("path"), "origin": http.get("origin")} if http else {}),
    )
    
    # Configurar responder
    responder = Responder(is_http=is_http, cors_origin=CONFIG.allowed_origin)
    
    # Preflight CORS
    method = _get_http_method(event)
    if is_http and method.upper() == "OPTIONS":
        logger.event(
            "🛡️ preflight",
            id=reference_id,
            fn=fn,
            method=method,
            path=(http.get("path") if isinstance(http, dict) else None),
            origin=(http.get("origin") if isinstance(http, dict) else None),
        )
        return responder.preflight()
    
    # Configurar clientes AWS (solo para logging)
    cloudwatch_client, lambda_client = make_boto_clients(region=CONFIG.region)
    
    # Crear controller
    controller = QAController(CONFIG, logger)
    
    try:
        # Procesar request
        result = controller.handle_request(body)
        
        # Calcular duración
        duration_ms = int((perf_counter() - start) * 1000)
        
        # Determinar status code
        status_code = 200 if result.get("success", False) else 400
        
        # Log resultado
        logger.event(
            "✅ qa.done",
            id=reference_id,
            fn=fn,
            status=status_code,
            success=result.get("success", False),
            ms=duration_ms,
            preguntas_count=len(result.get("qa_resultados", [])),
        )
        
        # Retornar respuesta
        return responder.respond(status_code, result)
        
    except Exception as e:
        # Manejo de errores
        duration_ms = int((perf_counter() - start) * 1000)
        
        logger.event(
            "❌ qa.error",
            err=str(e),
            id=reference_id,
            fn=fn,
            status=500,
            ms=duration_ms
        )
        
        # Respuesta de error
        error_response = {
            "success": False,
            "reference_id": reference_id,
            "error": {
                "codigo": "MODEL_ERROR",
                "detalle": str(e)
            }
        }
        
        return responder.respond(500, error_response)
