#!/usr/bin/env python3
"""
Script para probar la estructura del proyecto sin necesidad de API key
"""

import json
import sys
from pathlib import Path

# Agregar directorio padre al path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_imports():
    """Prueba que todos los imports funcionen correctamente"""
    print("🧪 Probando imports...")
    
    try:
        from config import default_config
        print("✅ config.py importado correctamente")
        
        from app_logging import get_app_logger
        print("✅ app_logging.py importado correctamente")
        
        from aws_clients import make_boto_clients
        print("✅ aws_clients.py importado correctamente")
        
        from http_gateway import parse_body, Responder
        print("✅ http_gateway.py importado correctamente")
        
        from qa_service.validator import QAValidator
        print("✅ qa_service.validator importado correctamente")
        
        from qa_service.controller import QAController
        print("✅ qa_service.controller importado correctamente")
        
        from call_llm.qa_schemas import qa_input_schema, qa_output_schema
        print("✅ call_llm.qa_schemas importado correctamente")
        
        from call_llm.qa_parser import qa_parser
        print("✅ call_llm.qa_parser importado correctamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en imports: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_config():
    """Prueba la configuración"""
    print("\n🔧 Probando configuración...")
    
    try:
        from config import default_config
        
        config = default_config()
        print(f"✅ Config creada: max_preguntas={config.max_preguntas}")
        print(f"✅ Modelo por defecto: {config.default_model}")
        print(f"✅ Timeout: {config.openai_timeout}s")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en configuración: {str(e)}")
        return False


def test_validator():
    """Prueba el validador"""
    print("\n🔍 Probando validador...")
    
    try:
        from config import default_config
        from qa_service.validator import QAValidator
        
        config = default_config()
        validator = QAValidator(config)
        
        # Test con datos válidos
        valid_request = {
            "texto_contrato": "Este es un contrato de prueba con suficiente texto para pasar la validación mínima de caracteres requeridos.",
            "reference_id": "test-001",
            "qa": {
                "preguntas": [
                    "¿Cuál es el objeto del contrato?",
                    "¿Quiénes son las partes?"
                ]
            }
        }
        
        result = validator.validate_request(valid_request)
        if result.get("valid"):
            print("✅ Validación de request válido: OK")
        else:
            print(f"❌ Validación falló: {result.get('error')}")
            return False
        
        # Test con datos inválidos
        invalid_request = {
            "texto_contrato": "Muy corto",
            "reference_id": "",
            "qa": {
                "preguntas": []
            }
        }
        
        result = validator.validate_request(invalid_request)
        if not result.get("valid"):
            print("✅ Validación de request inválido: OK (rechazado como esperado)")
        else:
            print("❌ Validación debería haber fallado")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error en validador: {str(e)}")
        return False


def test_schemas():
    """Prueba los schemas"""
    print("\n📋 Probando schemas...")
    
    try:
        from call_llm.qa_schemas import qa_input_schema, qa_output_schema
        
        input_schema = qa_input_schema()
        output_schema = qa_output_schema()
        
        print(f"✅ Input schema: {len(input_schema.get('properties', {}))} propiedades")
        print(f"✅ Output schema: {len(output_schema.get('properties', {}))} propiedades")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en schemas: {str(e)}")
        return False


def test_parser():
    """Prueba el parser de respuestas"""
    print("\n🔧 Probando parser...")
    
    try:
        from call_llm.qa_parser import qa_parser
        
        # Test con JSON válido
        valid_json = '''
        {
            "qa_resultados": [
                {
                    "pregunta_orden": 1,
                    "pregunta": "¿Cuál es el objeto?",
                    "respuesta": "Prestación de servicios",
                    "confianza": 0.9
                }
            ]
        }
        '''
        
        parsed, error = qa_parser.parse_any(valid_json)
        if parsed:
            print("✅ Parser JSON válido: OK")
        else:
            print(f"❌ Parser falló: {error}")
            return False
        
        # Test con JSON inválido
        invalid_json = "esto no es json válido"
        parsed, error = qa_parser.parse_any(invalid_json)
        if not parsed:
            print("✅ Parser JSON inválido: OK (rechazado como esperado)")
        else:
            print("❌ Parser debería haber fallado")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error en parser: {str(e)}")
        return False


def test_http_gateway():
    """Prueba el HTTP gateway"""
    print("\n🌐 Probando HTTP gateway...")
    
    try:
        from http_gateway import parse_body, Responder
        
        # Test evento directo
        direct_event = {
            "texto_contrato": "Contrato de prueba",
            "reference_id": "test-001",
            "qa": {"preguntas": ["¿Qué es esto?"]}
        }
        
        body, is_http = parse_body(direct_event)
        if not is_http and body == direct_event:
            print("✅ Parse evento directo: OK")
        else:
            print("❌ Parse evento directo falló")
            return False
        
        # Test evento HTTP
        http_event = {
            "body": json.dumps(direct_event),
            "httpMethod": "POST"
        }
        
        body, is_http = parse_body(http_event)
        if is_http and body.get("reference_id") == "test-001":
            print("✅ Parse evento HTTP: OK")
        else:
            print("❌ Parse evento HTTP falló")
            return False
        
        # Test responder
        responder = Responder(is_http=True)
        response = responder.respond(200, {"success": True})
        if response.get("statusCode") == 200:
            print("✅ Responder HTTP: OK")
        else:
            print("❌ Responder HTTP falló")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error en HTTP gateway: {str(e)}")
        return False


def main():
    """Función principal de testing"""
    print("🧪 Testing QA Personalizado Service - Estructura")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_config,
        test_validator,
        test_schemas,
        test_parser,
        test_http_gateway,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Resultados: {passed}/{total} tests pasaron")
    
    if passed == total:
        print("🎉 ¡Todos los tests pasaron! La estructura está correcta.")
        print("\n📝 Próximos pasos:")
        print("1. Configurar OPENAI_API_KEY en .env")
        print("2. Ejecutar: python local/test_local.py")
        return 0
    else:
        print("❌ Algunos tests fallaron. Revisar errores arriba.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
