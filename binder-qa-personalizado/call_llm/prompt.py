import os
from typing import Optional


def read_qa_prompt_text() -> Optional[str]:
    """
    Lee el prompt de QA desde archivo o variable de entorno.
    
    Search order:
    1) PROMPT_FILE (variable de entorno)
    2) qa_prompt.txt (en directorio raíz)
    3) call_llm/qa_prompt.txt (en directorio call_llm)
    """
    # 1) Variable de entorno
    path = os.environ.get("PROMPT_FILE")
    if path:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            pass
    
    here = os.path.dirname(__file__)
    
    # 2) Directorio raíz
    try:
        repo_root = os.path.abspath(os.path.join(here, ".."))
        prompt_path = os.path.join(repo_root, "qa_prompt.txt")
        if os.path.isfile(prompt_path):
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read()
    except Exception:
        pass
    
    # 3) Directorio call_llm
    try:
        prompt_path2 = os.path.join(here, "qa_prompt.txt")
        if os.path.isfile(prompt_path2):
            with open(prompt_path2, "r", encoding="utf-8") as f:
                return f.read()
    except Exception:
        pass
    
    # 4) Prompt por defecto
    return get_default_qa_prompt()


def get_default_qa_prompt() -> str:
    """Prompt por defecto para QA de contratos"""
    return """Eres un experto en análisis de contratos y documentos legales.

TAREA: Analizar el contrato proporcionado y responder las preguntas específicas de manera precisa y estructurada.

INSTRUCCIONES:
1. Lee cuidadosamente todo el texto del contrato
2. Para cada pregunta, busca la información relevante en el contrato
3. Proporciona respuestas claras y específicas
4. Si no encuentras información, responde "No se encontró información en el contrato"
5. Incluye nivel de confianza (0.0 a 1.0) basado en la claridad de la información
6. Si se solicita razonamiento, explica brevemente dónde encontraste la información

FORMATO DE RESPUESTA:
- Responde ÚNICAMENTE con un JSON válido
- La estructura debe ser: {"qa_resultados": [{"pregunta_orden": 1, "pregunta": "...", "respuesta": "...", "confianza": 0.8, "razonamiento": "..."}]}
- Las respuestas deben mantener el mismo orden que las preguntas de entrada
- Usa confianza alta (0.8-1.0) para información explícita y clara
- Usa confianza media (0.5-0.7) para información inferida o parcial
- Usa confianza baja (0.1-0.4) para información incierta o ambigua

CONTRATO:
{texto_contrato}

PREGUNTAS:
{preguntas_formateadas}

RESPUESTA JSON:"""


def format_qa_prompt(texto_contrato: str, preguntas: list, incluir_razonamiento: bool = False) -> str:
    """
    Formatea el prompt con el contrato y preguntas específicas.
    
    Args:
        texto_contrato: Texto del contrato a analizar
        preguntas: Lista de preguntas
        incluir_razonamiento: Si incluir campo razonamiento
        
    Returns:
        Prompt formateado
    """
    prompt_template = read_qa_prompt_text()
    if not prompt_template:
        prompt_template = get_default_qa_prompt()
    
    # Formatear preguntas
    preguntas_formateadas = ""
    for i, pregunta in enumerate(preguntas, 1):
        preguntas_formateadas += f"{i}. {pregunta}\n"
    
    # Reemplazar placeholders
    formatted = prompt_template.format(
        texto_contrato=texto_contrato,
        preguntas_formateadas=preguntas_formateadas.strip()
    )
    
    # Agregar instrucción sobre razonamiento si es necesario
    if incluir_razonamiento:
        formatted += "\n\nIMPORTANTE: Incluye el campo 'razonamiento' en cada respuesta explicando brevemente dónde encontraste la información."
    else:
        formatted += "\n\nIMPORTANTE: NO incluyas el campo 'razonamiento' en las respuestas."
    
    return formatted
