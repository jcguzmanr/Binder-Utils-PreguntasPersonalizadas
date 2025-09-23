import os
from typing import Optional


def load_env_openai_key() -> Optional[str]:
    """
    Carga OPENAI_API_KEY desde variables de entorno.
    
    Para desarrollo local, intenta cargar desde archivo .env en el directorio raíz.
    """
    key = os.environ.get("OPENAI_API_KEY")
    if key:
        return key
    
    # Best-effort .env en directorio raíz para desarrollo local
    try:
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        env_path = os.path.join(base, ".env")
        if os.path.isfile(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                for raw in f:
                    line = raw.strip()
                    if not line or line.startswith("#"):
                        continue
                    if line.startswith("OPENAI_API_KEY="):
                        val = line.split("=", 1)[1].strip()
                        # Remover comillas si las hay
                        if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                            val = val[1:-1]
                        if val:
                            os.environ["OPENAI_API_KEY"] = val
                            return val
    except Exception:
        pass
    
    return None
