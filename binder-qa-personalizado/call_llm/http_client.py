import json
import ssl
from typing import Optional, Tuple, Dict, Any
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import socket


class HTTPClient:
    """Cliente HTTP personalizado para llamadas a OpenAI"""
    
    def __init__(self, api_key: str, timeout: int):
        self.api_key = api_key
        self.timeout = timeout
        self._headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
    
    def post(self, url: str, body: Dict[str, Any]) -> Tuple[Optional[int], Optional[str], Optional[str]]:
        """
        Realiza POST request a OpenAI API.
        
        Returns:
            Tuple con (status_code, response_body, error_message)
        """
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        req = Request(url, data=data, headers=self._headers, method="POST")
        
        # Configurar SSL context
        ctx = ssl.create_default_context()
        
        try:
            with urlopen(req, timeout=self.timeout, context=ctx) as resp:
                raw = resp.read().decode("utf-8", errors="replace")
                return resp.getcode(), raw, None
                
        except HTTPError as e:
            try:
                raw = e.read().decode("utf-8", errors="replace")
            except Exception:
                raw = ""
            return e.code, raw, f"HTTP {e.code}: {getattr(e, 'reason', '')}"
            
        except socket.timeout:
            return None, None, "Request timeout"
            
        except Exception as e:
            return None, None, str(e)

