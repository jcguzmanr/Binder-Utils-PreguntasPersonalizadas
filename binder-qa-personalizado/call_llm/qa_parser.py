import json
import re
from typing import Any, Dict, List, Optional, Tuple


class QAResponseParser:
    """Parser para respuestas de QA de OpenAI"""
    
    def __init__(self):
        self.json_pattern = re.compile(r'```json\s*(.*?)\s*```', re.DOTALL | re.IGNORECASE)
        self.json_pattern_no_backticks = re.compile(r'\{.*\}', re.DOTALL)
    
    def parse_any(self, raw_response: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Intenta parsear respuesta JSON de OpenAI.
        
        Returns:
            Tuple con (parsed_data, error_message)
        """
        if not raw_response or not isinstance(raw_response, str):
            return None, "Empty or invalid response"
        
        # Limpiar respuesta
        cleaned = raw_response.strip()
        
        # Intentar diferentes estrategias de parsing
        strategies = [
            self._parse_json_with_backticks,
            self._parse_json_direct,
            self._parse_json_array,
            self._parse_json_cleanup
        ]
        
        for strategy in strategies:
            try:
                result = strategy(cleaned)
                if result is not None:
                    return result, None
            except Exception as e:
                continue
        
        return None, "Could not parse JSON response"
    
    def _parse_json_with_backticks(self, text: str) -> Optional[Dict[str, Any]]:
        """Parsear JSON dentro de bloques ```json```"""
        match = self.json_pattern.search(text)
        if match:
            json_str = match.group(1).strip()
            return json.loads(json_str)
        return None
    
    def _parse_json_direct(self, text: str) -> Optional[Dict[str, Any]]:
        """Parsear JSON directo"""
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return None
    
    def _parse_json_array(self, text: str) -> Optional[Dict[str, Any]]:
        """Parsear si la respuesta es un array de objetos"""
        try:
            data = json.loads(text)
            if isinstance(data, list) and len(data) > 0:
                # Si es array, convertir a formato esperado
                return {"qa_resultados": data}
            return None
        except json.JSONDecodeError:
            return None
    
    def _parse_json_cleanup(self, text: str) -> Optional[Dict[str, Any]]:
        """Parsear con limpieza de texto extra"""
        # Buscar objeto JSON en el texto
        match = self.json_pattern_no_backticks.search(text)
        if match:
            json_str = match.group(0)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                return None
        return None
    
    def normalize_qa_responses(self, data: Any, preguntas: List[str], 
                             incluir_razonamiento: bool = False) -> List[Dict[str, Any]]:
        """
        Normaliza respuestas de QA a formato esperado.
        
        Args:
            data: Datos parseados de OpenAI
            preguntas: Lista original de preguntas
            incluir_razonamiento: Si incluir campo razonamiento
            
        Returns:
            Lista de respuestas normalizadas
        """
        try:
            if not isinstance(data, dict):
                data = {}
            
            # Extraer qa_resultados
            qa_resultados = data.get("qa_resultados", [])
            if not isinstance(qa_resultados, list):
                qa_resultados = []
            
            # Normalizar respuestas
            normalized = []
            for i, pregunta in enumerate(preguntas):
                pregunta_orden = i + 1
                
                # Buscar respuesta correspondiente
                respuesta_data = None
                if i < len(qa_resultados):
                    respuesta_data = qa_resultados[i]
                
                if not isinstance(respuesta_data, dict):
                    respuesta_data = {}
                
                # Extraer campos con validación
                respuesta = respuesta_data.get("respuesta", "No se encontró información en el contrato")
                confianza_raw = respuesta_data.get("confianza", 0.5)
                razonamiento = respuesta_data.get("razonamiento", "")
                
                # Validar y convertir confianza
                try:
                    confianza = float(confianza_raw)
                    if confianza < 0 or confianza > 1:
                        confianza = 0.5
                except (ValueError, TypeError):
                    confianza = 0.5
                
                # Crear respuesta normalizada
                normalized_response = {
                    "pregunta_orden": pregunta_orden,
                    "pregunta": str(pregunta),
                    "respuesta": str(respuesta),
                    "confianza": confianza
                }
                
                # Agregar razonamiento si se solicita
                if incluir_razonamiento and razonamiento:
                    normalized_response["razonamiento"] = str(razonamiento)
                
                normalized.append(normalized_response)
            
            return normalized
            
        except Exception as e:
            # En caso de error, retornar respuestas básicas
            normalized = []
            for i, pregunta in enumerate(preguntas):
                normalized.append({
                    "pregunta_orden": i + 1,
                    "pregunta": str(pregunta),
                    "respuesta": "Error en el procesamiento de la respuesta",
                    "confianza": 0.0
                })
            return normalized


# Instancia global del parser
qa_parser = QAResponseParser()
