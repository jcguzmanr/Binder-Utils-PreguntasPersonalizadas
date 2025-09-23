from typing import Dict, Any, List


def qa_input_schema() -> Dict[str, Any]:
    """Schema para validar entrada de QA personalizado"""
    return {
        "type": "object",
        "properties": {
            "texto_contrato": {
                "type": "string",
                "minLength": 1,
                "description": "Texto completo del contrato a analizar"
            },
            "reference_id": {
                "type": "string",
                "minLength": 1,
                "description": "Identificador único de la ejecución"
            },
            "qa": {
                "type": "object",
                "properties": {
                    "webhook_url": {
                        "type": "string",
                        "format": "uri",
                        "description": "URL opcional para webhook"
                    },
                    "incluir_razonamiento": {
                        "type": "boolean",
                        "description": "Si incluir campo razonamiento en respuestas"
                    },
                    "preguntas": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "maxLength": 300,
                            "minLength": 1
                        },
                        "maxItems": 50,
                        "minItems": 1,
                        "description": "Lista de preguntas a responder"
                    }
                },
                "required": ["preguntas"],
                "additionalProperties": False
            }
        },
        "required": ["texto_contrato", "reference_id", "qa"],
        "additionalProperties": False
    }


def qa_output_schema() -> Dict[str, Any]:
    """Schema para estructura de salida QA"""
    return {
        "type": "object",
        "properties": {
            "success": {
                "type": "boolean",
                "description": "Indica si la operación fue exitosa"
            },
            "reference_id": {
                "type": "string",
                "description": "ID de referencia de la ejecución"
            },
            "qa_resultados": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "pregunta_orden": {
                            "type": "integer",
                            "minimum": 1,
                            "description": "Orden de la pregunta (1-based)"
                        },
                        "pregunta": {
                            "type": "string",
                            "description": "Texto de la pregunta original"
                        },
                        "respuesta": {
                            "type": "string",
                            "description": "Respuesta extraída del contrato"
                        },
                        "confianza": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 1.0,
                            "description": "Nivel de confianza de la respuesta (0.0-1.0)"
                        },
                        "razonamiento": {
                            "type": "string",
                            "description": "Explicación de cómo se obtuvo la respuesta"
                        }
                    },
                    "required": ["pregunta_orden", "pregunta", "respuesta", "confianza"],
                    "additionalProperties": False
                },
                "description": "Resultados de las preguntas procesadas"
            },
            "metadatos": {
                "type": "object",
                "properties": {
                    "modelo": {
                        "type": "string",
                        "description": "Modelo de OpenAI utilizado"
                    },
                    "latencia_ms": {
                        "type": "integer",
                        "minimum": 0,
                        "description": "Tiempo de procesamiento en milisegundos"
                    },
                    "modo": {
                        "type": "string",
                        "enum": ["sync"],
                        "description": "Modo de ejecución"
                    },
                    "webhook_disparado": {
                        "type": "boolean",
                        "description": "Si se disparó webhook"
                    }
                },
                "required": ["modelo", "latencia_ms", "modo", "webhook_disparado"],
                "additionalProperties": False
            }
        },
        "required": ["success", "reference_id", "qa_resultados", "metadatos"],
        "additionalProperties": False
    }


def qa_error_schema() -> Dict[str, Any]:
    """Schema para respuestas de error"""
    return {
        "type": "object",
        "properties": {
            "success": {
                "type": "boolean",
                "const": False
            },
            "reference_id": {
                "type": ["string", "null"],
                "description": "ID de referencia si está disponible"
            },
            "error": {
                "type": "object",
                "properties": {
                    "codigo": {
                        "type": "string",
                        "enum": ["BAD_REQUEST", "TIMEOUT", "MODEL_ERROR", "WEBHOOK_ERROR"],
                        "description": "Código de error específico"
                    },
                    "detalle": {
                        "type": "string",
                        "description": "Descripción legible del error"
                    }
                },
                "required": ["codigo", "detalle"],
                "additionalProperties": False
            }
        },
        "required": ["success", "error"],
        "additionalProperties": False
    }
