#!/usr/bin/env python3
"""
Script simple para probar y ver respuestas
"""

import json
import os
import sys
from pathlib import Path

# Agregar directorio padre al path para imports
sys.path.insert(0, str(Path(__file__).parent))

from lambda_function import lambda_handler


def main():
    # Leer un contrato
    contract_files = list(Path("contratos").glob("*.txt"))
    if not contract_files:
        print("❌ No hay archivos de contratos")
        return
    
    contract_file = contract_files[0]
    print(f"📄 Probando con: {contract_file.name}")
    
    with open(contract_file, 'r', encoding='utf-8') as f:
        contract_text = f.read()
    
    print(f"📊 Tamaño: {len(contract_text)} caracteres")
    
    # Evento de prueba
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
    
    # Ejecutar
    result = lambda_handler(event, context)
    
    print("\n📋 RESULTADO:")
    print("=" * 50)
    
    # Mostrar resultado completo para debug
    print("🔍 Resultado completo:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # Verificar si es exitoso
    if result.get("success"):
        print("\n✅ ANÁLISIS EXITOSO!")
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
        print("❌ ANÁLISIS FALLÓ")
        error = result.get("error", {})
        print(f"   Código: {error.get('codigo', 'N/A')}")
        print(f"   Detalle: {error.get('detalle', 'N/A')}")


if __name__ == "__main__":
    main()
