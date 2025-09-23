#!/usr/bin/env python3
"""
Script simple para probar un solo contrato y ver las respuestas
"""

import json
import os
import sys
from pathlib import Path

# Agregar directorio padre al path para imports
sys.path.insert(0, str(Path(__file__).parent))

from lambda_function import lambda_handler


def test_single_contract():
    """Prueba con un solo contrato"""
    
    # Leer un contrato simple
    contract_files = list(Path("contratos").glob("*.txt"))
    if not contract_files:
        print("❌ No hay archivos de contratos")
        return
    
    # Tomar el primer archivo
    contract_file = contract_files[0]
    print(f"📄 Probando con: {contract_file.name}")
    
    # Leer contrato
    with open(contract_file, 'r', encoding='utf-8') as f:
        contract_text = f.read()
    
    print(f"📊 Tamaño: {len(contract_text)} caracteres")
    
    # Crear evento de prueba
    event = {
        "texto_contrato": contract_text,
        "reference_id": "test-001",
        "qa": {
            "incluir_razonamiento": True,
            "preguntas": [
                "¿Cuál es el objeto del contrato?",
                "¿Quiénes son las partes involucradas?",
                "¿Cuál es el monto o valor del contrato?"
            ]
        }
    }
    
    # Contexto mock
    class MockContext:
        def __init__(self):
            self.function_name = "qa-test"
    
    context = MockContext()
    
    print("\n🚀 Ejecutando análisis...")
    
    try:
        # Ejecutar
        result = lambda_handler(event, context)
        
        print("\n📋 RESULTADO:")
        print("=" * 50)
        
        # Debug: mostrar estructura del resultado (solo si hay error)
        if not result.get("success"):
            print(f"🔍 Tipo de resultado: {type(result)}")
            print(f"🔍 Claves del resultado: {list(result.keys()) if isinstance(result, dict) else 'No es dict'}")
        
        if isinstance(result, dict):
            if result.get("statusCode") == 200:
                body = json.loads(result["body"])
                
                if body.get("success"):
                    print("✅ Análisis exitoso!")
                    print(f"🆔 Reference ID: {body.get('reference_id')}")
                    
                    metadatos = body.get("metadatos", {})
                    print(f"🤖 Modelo: {metadatos.get('modelo', 'N/A')}")
                    print(f"⏱️  Latencia: {metadatos.get('latencia_ms', 'N/A')} ms")
                    
                    qa_resultados = body.get("qa_resultados", [])
                    print(f"💬 Respuestas: {len(qa_resultados)}")
                    
                    print("\n📝 RESPUESTAS:")
                    print("-" * 30)
                    
                    for i, respuesta in enumerate(qa_resultados, 1):
                        print(f"\n{i}. {respuesta.get('pregunta', 'N/A')}")
                        print(f"   📝 {respuesta.get('respuesta', 'N/A')}")
                        print(f"   🎯 Confianza: {respuesta.get('confianza', 0):.2f}")
                        if respuesta.get('razonamiento'):
                            print(f"   💭 Razonamiento: {respuesta.get('razonamiento')}")
                    
                else:
                    print("❌ Análisis falló")
                    error = body.get("error", {})
                    print(f"   Código: {error.get('codigo', 'N/A')}")
                    print(f"   Detalle: {error.get('detalle', 'N/A')}")
            else:
                print(f"❌ Error HTTP: {result.get('statusCode')}")
                print(f"   Body: {result.get('body', 'N/A')}")
        else:
            # Resultado directo (no HTTP)
            if result.get("success"):
                print("✅ Análisis exitoso!")
                print(f"🆔 Reference ID: {result.get('reference_id')}")
                
                metadatos = result.get("metadatos", {})
                print(f"🤖 Modelo: {metadatos.get('modelo', 'N/A')}")
                print(f"⏱️  Latencia: {metadatos.get('latencia_ms', 'N/A')} ms")
                
                qa_resultados = result.get("qa_resultados", [])
                print(f"💬 Respuestas: {len(qa_resultados)}")
                
                print("\n📝 RESPUESTAS:")
                print("-" * 30)
                
                for i, respuesta in enumerate(qa_resultados, 1):
                    print(f"\n{i}. {respuesta.get('pregunta', 'N/A')}")
                    print(f"   📝 {respuesta.get('respuesta', 'N/A')}")
                    print(f"   🎯 Confianza: {respuesta.get('confianza', 0):.2f}")
                    if respuesta.get('razonamiento'):
                        print(f"   💭 Razonamiento: {respuesta.get('razonamiento')}")
            else:
                print("❌ Análisis falló")
                error = result.get("error", {})
                print(f"   Código: {error.get('codigo', 'N/A')}")
                print(f"   Detalle: {error.get('detalle', 'N/A')}")
            
    except Exception as e:
        print(f"💥 Excepción: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_single_contract()
