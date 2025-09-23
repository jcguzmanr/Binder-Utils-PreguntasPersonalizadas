"""
Parser para extraer IDs de preguntas con formato [ID] pregunta
"""

import re
from typing import Dict, List, Tuple, Optional


def extract_question_id(question_string: str) -> Tuple[Optional[str], str]:
    """
    Extrae el ID y el texto de una pregunta con formato [ID] pregunta
    
    Args:
        question_string: String con formato "[ID] texto de la pregunta"
        
    Returns:
        Tuple con (id, pregunta_texto)
        Si no encuentra ID válido, retorna (None, question_string)
    """
    if not isinstance(question_string, str):
        return None, str(question_string)
    
    # Patrón para extraer [ID] del inicio
    pattern = r'^\[([A-Za-z0-9_\-]+)\]\s*(.+)$'
    match = re.match(pattern, question_string.strip())
    
    if match:
        question_id = match.group(1).strip()
        question_text = match.group(2).strip()
        
        # Validar que el ID no esté vacío y la pregunta tenga contenido
        if question_id and question_text:
            return question_id, question_text
    
    # Si no coincide el patrón, retornar sin ID
    return None, question_string.strip()


def parse_questions_with_ids(questions: List[str]) -> List[Dict[str, str]]:
    """
    Parsea una lista de preguntas con formato [ID] pregunta
    
    Args:
        questions: Lista de strings con formato "[ID] pregunta"
        
    Returns:
        Lista de diccionarios con {"id": "...", "pregunta": "..."}
    """
    parsed_questions = []
    
    for i, question_string in enumerate(questions):
        question_id, question_text = extract_question_id(question_string)
        
        # Si no se encontró ID, generar uno automático
        if question_id is None:
            question_id = f"P{i+1:03d}"
        
        parsed_questions.append({
            "id": question_id,
            "pregunta": question_text
        })
    
    return parsed_questions


def format_questions_for_prompt(questions: List[str]) -> str:
    """
    Formatea preguntas para el prompt de OpenAI
    
    Args:
        questions: Lista de strings con formato "[ID] pregunta"
        
    Returns:
        String formateado para el prompt
    """
    formatted_lines = []
    
    for i, question_string in enumerate(questions, 1):
        question_id, question_text = extract_question_id(question_string)
        
        if question_id:
            formatted_lines.append(f"{i}. [{question_id}] {question_text}")
        else:
            formatted_lines.append(f"{i}. {question_text}")
    
    return "\n".join(formatted_lines)


def validate_question_format(question_string: str) -> bool:
    """
    Valida si una pregunta tiene el formato correcto [ID] pregunta
    
    Args:
        question_string: String a validar
        
    Returns:
        True si tiene formato válido, False en caso contrario
    """
    if not isinstance(question_string, str):
        return False
    
    question_id, question_text = extract_question_id(question_string)
    return question_id is not None and len(question_text) > 0


# Ejemplos de uso y testing
if __name__ == "__main__":
    # Ejemplos de preguntas
    test_questions = [
        "[P001] ¿Cuál es el objeto del contrato?",
        "[MON002] ¿Cuál es el monto total?",
        "[DUR003] ¿Cuál es la duración?",
        "¿Esta pregunta no tiene ID?",  # Sin ID
        "[OBJ004] ¿Quiénes son las partes?",  # Con ID
    ]
    
    print("🧪 Probando parser de preguntas con IDs")
    print("=" * 50)
    
    for question in test_questions:
        question_id, question_text = extract_question_id(question)
        is_valid = validate_question_format(question)
        
        print(f"Original: {question}")
        print(f"  ID: {question_id}")
        print(f"  Texto: {question_text}")
        print(f"  Válido: {is_valid}")
        print()
    
    print("📋 Preguntas parseadas:")
    parsed = parse_questions_with_ids(test_questions)
    for p in parsed:
        print(f"  [{p['id']}] {p['pregunta']}")
    
    print("\n📝 Formato para prompt:")
    formatted = format_questions_for_prompt(test_questions)
    print(formatted)
