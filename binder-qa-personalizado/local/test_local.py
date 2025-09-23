#!/usr/bin/env python3
"""
Script para testing local del servicio QA personalizado
"""

import json
import os
import sys
from pathlib import Path

# Agregar directorio padre al path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from lambda_function import lambda_handler


def create_test_event():
    """Crea evento de prueba para QA"""
    return {
        "texto_contrato": """
        CONTRATO DE PRESTACIÓN DE SERVICIOS
        
        Entre los suscritos, JUAN CARLOS PÉREZ GARCÍA, identificado con DNI 12345678, 
        domiciliado en Av. Principal 123, Lima, en adelante "EL PRESTADOR", y 
        EMPRESA ABC S.A.C., con RUC 20123456789, domiciliada en Jr. Comercial 456, 
        Lima, en adelante "EL CONTRATANTE", se celebra el presente contrato de 
        prestación de servicios con las siguientes cláusulas:
        
        PRIMERA: OBJETO
        El objeto del presente contrato es la prestación de servicios de consultoría 
        en tecnología por parte del PRESTADOR a favor del CONTRATANTE.
        
        SEGUNDA: REMUNERACIÓN
        Por los servicios prestados, el CONTRATANTE pagará al PRESTADOR la suma de 
        S/ 5,000.00 (cinco mil soles) mensuales, los cuales serán cancelados hasta 
        el día 30 de cada mes.
        
        TERCERA: VIGENCIA
        El presente contrato tendrá una duración de 12 (doce) meses, contados a partir 
        del 1 de enero de 2024, pudiendo ser renovado por períodos iguales de mutuo 
        acuerdo entre las partes.
        
        CUARTA: CONFIDENCIALIDAD
        Las partes se comprometen a mantener la más estricta confidencialidad sobre 
        toda la información que se intercambie en virtud del presente contrato.
        
        QUINTA: FIRMAS
        En señal de conformidad, se firma el presente contrato en Lima, a los 15 días 
        del mes de diciembre de 2023.
        """,
        "reference_id": "test-001",
        "qa": {
            "incluir_razonamiento": True,
            "preguntas": [
                "¿Cuál es el monto de la remuneración mensual?",
                "¿Cuál es la fecha de inicio del contrato?",
                "¿Existe cláusula de confidencialidad?",
                "¿Cuál es la duración del contrato?",
                "¿Quién es el prestador de servicios?"
            ]
        }
    }


def create_test_context():
    """Crea contexto de prueba para Lambda"""
    class MockContext:
        def __init__(self):
            self.function_name = "qa-personalizado-test"
            self.function_version = "$LATEST"
            self.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:qa-personalizado-test"
            self.memory_limit_in_mb = 128
            self.remaining_time_in_millis = 30000
    
    return MockContext()


def main():
    """Función principal para testing local"""
    print("🧪 Testing QA Personalizado Service")
    print("=" * 50)
    
    # Verificar API key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY no encontrada en variables de entorno")
        print("   Crea un archivo .env en el directorio raíz con:")
        print("   OPENAI_API_KEY=tu_api_key_aqui")
        return 1
    
    print(f"✅ OPENAI_API_KEY encontrada: {api_key[:10]}...")
    
    # Crear evento y contexto de prueba
    event = create_test_event()
    context = create_test_context()
    
    print(f"📋 Evento de prueba creado con {len(event['qa']['preguntas'])} preguntas")
    print(f"📄 Texto del contrato: {len(event['texto_contrato'])} caracteres")
    
    print("\n🚀 Ejecutando lambda_handler...")
    print("-" * 30)
    
    try:
        # Ejecutar handler
        result = lambda_handler(event, context)
        
        print("✅ Resultado obtenido:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # Verificar resultado
        if isinstance(result, dict) and result.get("success"):
            print("\n🎉 Test exitoso!")
            qa_resultados = result.get("qa_resultados", [])
            print(f"📊 Respuestas generadas: {len(qa_resultados)}")
            
            for i, respuesta in enumerate(qa_resultados, 1):
                print(f"\n{i}. {respuesta.get('pregunta', 'N/A')}")
                print(f"   Respuesta: {respuesta.get('respuesta', 'N/A')}")
                print(f"   Confianza: {respuesta.get('confianza', 'N/A')}")
                if respuesta.get('razonamiento'):
                    print(f"   Razonamiento: {respuesta.get('razonamiento', 'N/A')}")
        else:
            print("\n❌ Test falló")
            if isinstance(result, dict):
                error = result.get("error", {})
                print(f"   Código: {error.get('codigo', 'N/A')}")
                print(f"   Detalle: {error.get('detalle', 'N/A')}")
        
        return 0
        
    except Exception as e:
        print(f"\n💥 Error durante la ejecución: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
