"""
Lambda function para procesar mensajes de SQS de QA personalizado.
Este handler procesa mensajes de cola de forma asíncrona.
"""

import json
import os
import sys
from typing import Dict, Any, List, Optional, Tuple

# Agregar el directorio actual al path para imports
sys.path.insert(0, os.path.dirname(__file__))

from app_logging import AppLogger
from config import Config
from qa_service.controller import QAController

# Configuración global
CONFIG = Config()
logger = AppLogger(CONFIG)

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handler principal de Lambda para procesar mensajes de SQS.
    
    Args:
        event: Evento de SQS con mensajes
        context: Contexto de Lambda
        
    Returns:
        Dict con resultado del procesamiento
    """
    try:
        logger.event("processor.lambda_start", 
                    request_id=context.aws_request_id,
                    event_keys=list(event.keys()))
        
        # Procesar cada mensaje de SQS
        results = []
        records = event.get("Records", [])
        
        logger.event("processor.records_count", count=len(records))
        
        for record in records:
            try:
                # Extraer datos del mensaje
                message_body = record.get("body", "{}")
                message_data = json.loads(message_body)
                
                logger.event("processor.message_received", 
                           message_id=record.get("messageId"),
                           body_preview=str(message_data)[:200])
                
                # Procesar mensaje individual
                result = process_sqs_message(message_data)
                results.append(result)
                
            except Exception as e:
                logger.event("processor.record_error", 
                           error=str(e),
                           record=record)
                results.append({
                    'success': False,
                    'error': str(e)
                })
        
        # Respuesta final
        response = {
            'statusCode': 200,
            'body': json.dumps({
                'processed': len(results),
                'results': results
            })
        }
        
        logger.event("processor.lambda_complete", 
                    processed_count=len(results),
                    success_count=sum(1 for r in results if r.get('success', False)))
        
        return response
        
    except Exception as e:
        logger.event("processor.lambda_error", error=str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }

def process_sqs_message(message_data):
    """Procesa un mensaje individual de SQS"""
    try:
        # Extraer datos del mensaje
        reference_id = message_data.get("reference_id")
        webhook_url = message_data.get("webhook_url")
        contract_text = message_data.get("contract_text", "")
        questions = message_data.get("questions", [])
        preguntas_parseadas = message_data.get("preguntas_parseadas", [])
        incluir_razonamiento = message_data.get("incluir_razonamiento", False)
        
        logger.event("processor.message_data_extracted",
                    id=reference_id,
                    webhook_url=webhook_url,
                    contract_length=len(contract_text),
                    questions_count=len(questions),
                    parsed_questions_count=len(preguntas_parseadas))
        
        if not reference_id:
            return {
                'success': False,
                'error': 'Missing reference_id'
            }
        
        if not contract_text:
            return {
                'success': False,
                'error': 'Missing contract_text'
            }
        
        if not questions:
            return {
                'success': False,
                'error': 'Missing questions'
            }
        
        # Crear controller y procesar QA
        controller = QAController(CONFIG, logger)
        
        # Preparar body para el controller
        body = {
            "contract_text": contract_text,
            "questions": questions,
            "preguntas_parseadas": preguntas_parseadas,
            "incluir_razonamiento": incluir_razonamiento,
            "webhook_url": webhook_url
        }
        
        # Procesar QA (sin enviar webhook, ya se envió desde el API)
        qa_response = controller.process_qa_request(body, reference_id)
        
        if not qa_response.get("success", False):
            logger.event("processor.qa_failed", 
                        id=reference_id,
                        error=qa_response.get("error", {}))
            return {
                'success': False,
                'error': qa_response.get("error", {}).get("detalle", "QA processing failed")
            }
        
        # Usar la respuesta completa de QA que ya viene procesada con id, tipo y valores específicos
        webhook_response = {
            "success": True,
            "reference_id": reference_id,
            "qa_resultados": qa_response.get("qa_resultados", []),
            "metadatos": {
                "modelo": CONFIG.default_model,
                "latencia_ms": 0,  # Se calculará en el webhook
                "modo": "async",
                "webhook_disparado": False,
                "tipos_datos_procesados": [p.get("tipo", "Desconocido") for p in qa_response.get("qa_resultados", [])],
                "preguntas_procesadas": len(qa_response.get("qa_resultados", []))
            }
        }
        
        # En modo asíncrono, el webhook ya se envió desde el controller
        # No necesitamos enviarlo de nuevo desde el processor
        webhook_sent = qa_response.get("metadatos", {}).get("webhook_disparado", False)
        
        logger.event(
            "processor.webhook_status",
            id=reference_id,
            webhook_url=webhook_url,
            webhook_already_sent=webhook_sent,
            mode="async"
        )
        
        return {
            'success': True,
            'webhook_sent': webhook_sent,
            'reference_id': reference_id
        }
        
    except Exception as e:
        logger.event(
            "processor.message_processing_error",
            error=str(e),
            message_data=message_data
        )
        return {
            'success': False,
            'error': str(e)
        }
