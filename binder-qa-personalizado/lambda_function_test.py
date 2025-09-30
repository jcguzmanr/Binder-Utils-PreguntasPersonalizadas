import json
import os
import sys

# Agregar el directorio actual al path para imports
sys.path.insert(0, os.path.dirname(__file__))

def lambda_handler(event, context):
    """Test básico para verificar imports"""
    try:
        # Test imports básicos
        from config import QAConfig
        from app_logging import AppLogger
        
        config = QAConfig()
        logger = AppLogger(config)
        
        logger.event("test.basic_imports_success")
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            },
            'body': json.dumps({
                'success': True,
                'message': 'Basic imports working',
                'config_model': config.default_model
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            },
            'body': json.dumps({
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            })
        }
