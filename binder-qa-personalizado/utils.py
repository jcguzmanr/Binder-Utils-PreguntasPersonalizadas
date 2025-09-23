import json
import time
from typing import Dict, Any, Optional
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import ssl


def download_file(url: str, timeout: int = 30, max_bytes: int = 10 * 1024 * 1024) -> bytes:
    """
    Descarga un archivo desde URL con límites de tamaño y timeout.
    
    Args:
        url: URL del archivo
        timeout: Timeout en segundos
        max_bytes: Máximo de bytes a descargar
        
    Returns:
        Contenido del archivo como bytes
        
    Raises:
        Exception: Si hay error en la descarga
    """
    req = Request(url)
    ctx = ssl.create_default_context()
    
    with urlopen(req, timeout=timeout, context=ctx) as response:
        content_length = response.headers.get('Content-Length')
        
        if content_length and int(content_length) > max_bytes:
            raise Exception(f"File too large: {content_length} bytes (max: {max_bytes})")
        
        data = response.read(max_bytes + 1)
        if len(data) > max_bytes:
            raise Exception(f"File too large: {len(data)} bytes (max: {max_bytes})")
        
        return data


def post_json(url: str, data: Dict[str, Any], timeout: int = 30, 
              verify_ssl: bool = True, headers: Optional[Dict[str, str]] = None) -> int:
    """
    Envía POST request con JSON.
    
    Args:
        url: URL de destino
        data: Datos a enviar
        timeout: Timeout en segundos
        verify_ssl: Si verificar SSL
        headers: Headers adicionales
        
    Returns:
        Status code de la respuesta
        
    Raises:
        Exception: Si hay error en el request
    """
    json_data = json.dumps(data, ensure_ascii=False).encode('utf-8')
    
    request_headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Binder-QA-Service/1.0'
    }
    
    if headers:
        request_headers.update(headers)
    
    req = Request(url, data=json_data, headers=request_headers, method='POST')
    
    if verify_ssl:
        ctx = ssl.create_default_context()
    else:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    
    with urlopen(req, timeout=timeout, context=ctx) as response:
        return response.getcode()


def clean_text(text: str) -> str:
    """
    Limpia texto removiendo caracteres problemáticos.
    
    Args:
        text: Texto a limpiar
        
    Returns:
        Texto limpio
    """
    if not text:
        return ""
    
    # Remover caracteres de control excepto tab, newline, carriage return
    cleaned = ""
    for char in text:
        if ord(char) >= 32 or char in '\t\n\r':
            cleaned += char
    
    # Normalizar espacios en blanco múltiples
    import re
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    return cleaned.strip()


def format_duration_ms(start_time: float, end_time: Optional[float] = None) -> int:
    """
    Calcula duración en milisegundos.
    
    Args:
        start_time: Tiempo de inicio (time.perf_counter())
        end_time: Tiempo de fin (opcional, usa time.perf_counter() si no se proporciona)
        
    Returns:
        Duración en milisegundos
    """
    if end_time is None:
        end_time = time.perf_counter()
    
    return int((end_time - start_time) * 1000)


def safe_get(dictionary: Dict[str, Any], key: str, default: Any = None) -> Any:
    """
    Obtiene valor de diccionario de forma segura.
    
    Args:
        dictionary: Diccionario
        key: Clave (puede ser nested con dots)
        default: Valor por defecto
        
    Returns:
        Valor encontrado o default
    """
    if not isinstance(dictionary, dict):
        return default
    
    keys = key.split('.')
    value = dictionary
    
    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            return default
    
    return value


def validate_json_schema(data: Any, schema: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Validación básica de JSON schema.
    
    Args:
        data: Datos a validar
        schema: Schema JSON (básico)
        
    Returns:
        Tuple con (is_valid, error_message)
    """
    try:
        # Validación básica de tipo
        expected_type = schema.get('type')
        if expected_type:
            if expected_type == 'object' and not isinstance(data, dict):
                return False, f"Expected object, got {type(data).__name__}"
            elif expected_type == 'array' and not isinstance(data, list):
                return False, f"Expected array, got {type(data).__name__}"
            elif expected_type == 'string' and not isinstance(data, str):
                return False, f"Expected string, got {type(data).__name__}"
            elif expected_type == 'number' and not isinstance(data, (int, float)):
                return False, f"Expected number, got {type(data).__name__}"
            elif expected_type == 'boolean' and not isinstance(data, bool):
                return False, f"Expected boolean, got {type(data).__name__}"
        
        # Validación de propiedades requeridas
        required_fields = schema.get('required', [])
        if isinstance(data, dict):
            for field in required_fields:
                if field not in data:
                    return False, f"Missing required field: {field}"
        
        # Validación de propiedades
        properties = schema.get('properties', {})
        if isinstance(data, dict):
            for field, value in data.items():
                if field in properties:
                    field_schema = properties[field]
                    is_valid, error = validate_json_schema(value, field_schema)
                    if not is_valid:
                        return False, f"Field '{field}': {error}"
        
        return True, None
        
    except Exception as e:
        return False, f"Validation error: {str(e)}"
