"""
Lambda function para manejar requests de QA personalizado de forma asíncrona.
Este handler recibe requests, los envía a SQS y responde inmediatamente.
"""

import json
import os
import sys
from typing import Dict, Any, Optional

# Agregar el directorio actual al path para imports
sys.path.insert(0, os.path.dirname(__file__))

from app_logging import AppLogger
from config import Config
from qa_service.controller import QAController
from aws_clients import get_sqs_client

# Configuración global
CONFIG = Config()
logger = AppLogger(CONFIG)

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handler principal de Lambda para requests asíncronos de QA.
    
    Args:
        event: Evento de API Gateway
        context: Contexto de Lambda
        
    Returns:
        Dict con respuesta HTTP
    """
    try:
        # Configurar CORS
        headers = {
            'Access-Control-Allow-Origin': CONFIG.allowed_origin,
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'POST,OPTIONS'
        }
        
        # Manejar preflight OPTIONS
        if event.get('httpMethod') == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({'message': 'CORS preflight'})
            }
        
        # Extraer datos del request
        try:
            if event.get('isBase64Encoded', False):
                import base64
                body = base64.b64decode(event.get('body', '')).decode('utf-8')
            else:
                body = event.get('body', '{}')
            
            request_data = json.loads(body) if body else {}
        except Exception as e:
            logger.event("async.request_parse_error", error=str(e))
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'success': False,
                    'error': {
                        'codigo': 'INVALID_REQUEST',
                        'detalle': 'Invalid JSON in request body'
                    }
                })
            }
        
        logger.event("async.request_received", 
                    request_id=context.aws_request_id,
                    body_keys=list(request_data.keys()))
        
        # Validar datos requeridos
        required_fields = ['contract_text', 'questions']
        missing_fields = [field for field in required_fields if not request_data.get(field)]
        
        if missing_fields:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'success': False,
                    'error': {
                        'codigo': 'MISSING_FIELDS',
                        'detalle': f'Missing required fields: {", ".join(missing_fields)}'
                    }
                })
            }
        
        # Generar reference_id si no se proporciona
        reference_id = request_data.get('reference_id')
        if not reference_id:
            import time
            reference_id = f"async-{int(time.time() * 1000)}"
        
        # Extraer datos del request
        contract_text = request_data.get('contract_text', '')
        questions = request_data.get('questions', [])
        preguntas_parseadas = request_data.get('preguntas_parseadas', [])
        incluir_razonamiento = request_data.get('incluir_razonamiento', False)
        webhook_url = request_data.get('webhook_url')
        
        logger.event("async.request_data_extracted",
                    id=reference_id,
                    contract_length=len(contract_text),
                    questions_count=len(questions),
                    parsed_questions_count=len(preguntas_parseadas),
                    webhook_url=webhook_url)
        
        # Validar longitud mínima del contrato
        if len(contract_text) < CONFIG.qa_min_chars_contrato:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'success': False,
                    'error': {
                        'codigo': 'CONTRACT_TOO_SHORT',
                        'detalle': f'Contract text must be at least {CONFIG.qa_min_chars_contrato} characters'
                    }
                })
            }
        
        # Validar número máximo de preguntas
        if len(questions) > CONFIG.qa_max_preguntas:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'success': False,
                    'error': {
                        'codigo': 'TOO_MANY_QUESTIONS',
                        'detalle': f'Maximum {CONFIG.qa_max_preguntas} questions allowed'
                    }
                })
            }
        
        # Enviar mensaje a SQS
        try:
            sqs_client = get_sqs_client()
            queue_url = os.environ.get('SQS_QUEUE_URL')
            
            if not queue_url:
                logger.event("async.sqs_queue_missing")
                return {
                    'statusCode': 500,
                    'headers': headers,
                    'body': json.dumps({
                        'success': False,
                        'error': {
                            'codigo': 'CONFIGURATION_ERROR',
                            'detalle': 'SQS queue URL not configured'
                        }
                    })
                }
            
            # Preparar mensaje para SQS
            sqs_message = {
                'reference_id': reference_id,
                'contract_text': contract_text,
                'questions': questions,
                'preguntas_parseadas': preguntas_parseadas,
                'incluir_razonamiento': incluir_razonamiento,
                'webhook_url': webhook_url
            }
            
            # Enviar a SQS
            response = sqs_client.send_message(
                QueueUrl=queue_url,
                MessageBody=json.dumps(sqs_message),
                MessageAttributes={
                    'reference_id': {
                        'StringValue': reference_id,
                        'DataType': 'String'
                    },
                    'webhook_url': {
                        'StringValue': webhook_url or '',
                        'DataType': 'String'
                    }
                }
            )
            
            message_id = response.get('MessageId')
            logger.event("async.sqs_message_sent", 
                        id=reference_id,
                        message_id=message_id,
                        queue_url=queue_url)
            
            # Respuesta exitosa
            return {
                'statusCode': 202,  # Accepted
                'headers': headers,
                'body': json.dumps({
                    'success': True,
                    'reference_id': reference_id,
                    'message_id': message_id,
                    'status': 'queued',
                    'message': 'Request queued for processing'
                })
            }
            
        except Exception as e:
            logger.event("async.sqs_error", 
                        id=reference_id,
                        error=str(e))
            return {
                'statusCode': 500,
                'headers': headers,
                'body': json.dumps({
                    'success': False,
                    'error': {
                        'codigo': 'QUEUE_ERROR',
                        'detalle': f'Failed to queue request: {str(e)}'
                    }
                })
            }
        
    except Exception as e:
        logger.event("async.lambda_error", error=str(e))
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': CONFIG.allowed_origin,
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            },
            'body': json.dumps({
                'success': False,
                'error': {
                    'codigo': 'INTERNAL_ERROR',
                    'detalle': str(e)
                }
            })
        }
