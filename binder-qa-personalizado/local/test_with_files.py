#!/usr/bin/env python3
"""
Script para probar el servicio QA con archivos de texto de la carpeta contratos/
"""

import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any

# Agregar directorio padre al path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from lambda_function import lambda_handler


def get_contract_files() -> List[str]:
    """Obtiene lista de archivos .txt en la carpeta contratos/"""
    contracts_dir = Path(__file__).parent.parent / "contratos"
    
    if not contracts_dir.exists():
        print(f"❌ Carpeta {contracts_dir} no existe")
        return []
    
    txt_files = list(contracts_dir.glob("*.txt"))
    return [str(f) for f in txt_files if f.name != "README.md"]


def read_contract_file(file_path: str) -> str:
    """Lee un archivo de contrato"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except UnicodeDecodeError:
        # Intentar con encoding diferente
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read().strip()
        except Exception as e:
            print(f"❌ Error leyendo {file_path}: {e}")
            return ""
    except Exception as e:
        print(f"❌ Error leyendo {file_path}: {e}")
        return ""


def create_test_questions() -> List[str]:
    """Crea lista de preguntas de prueba"""
    return [
        "¿Cuál es el objeto del contrato?",
        "¿Quiénes son las partes involucradas?",
        "¿Cuál es el monto o valor del contrato?",
        "¿Cuál es la duración o vigencia?",
        "¿Existe cláusula de confidencialidad?",
        "¿Cuáles son las obligaciones principales?",
        "¿Hay penalidades por incumplimiento?",
        "¿Cuál es la forma de pago?"
    ]


def test_single_contract(contract_text: str, filename: str, questions: List[str]) -> Dict[str, Any]:
    """Prueba un contrato individual"""
    print(f"\n📄 Procesando: {filename}")
    print(f"📊 Tamaño: {len(contract_text)} caracteres")
    print(f"❓ Preguntas: {len(questions)}")
    print("-" * 50)
    
    # Crear evento
    event = {
        "texto_contrato": contract_text,
        "reference_id": f"test-{filename.replace('.txt', '')}",
        "qa": {
            "incluir_razonamiento": True,
            "preguntas": questions
        }
    }
    
    # Contexto mock
    class MockContext:
        def __init__(self, filename: str):
            self.function_name = f"qa-test-{filename.replace('.txt', '')}"
    
    context = MockContext(filename)
    
    try:
        # Ejecutar análisis
        result = lambda_handler(event, context)
        
        if isinstance(result, dict) and result.get("success"):
            qa_resultados = result.get("qa_resultados", [])
            metadatos = result.get("metadatos", {})
            
            print(f"✅ Análisis exitoso!")
            print(f"🤖 Modelo: {metadatos.get('modelo', 'N/A')}")
            print(f"⏱️  Latencia: {metadatos.get('latencia_ms', 'N/A')} ms")
            print(f"💬 Respuestas: {len(qa_resultados)}")
            
            # Mostrar respuestas resumidas
            for i, respuesta in enumerate(qa_resultados[:3], 1):  # Solo primeras 3
                print(f"\n{i}. {respuesta.get('pregunta', 'N/A')[:50]}...")
                print(f"   📝 {respuesta.get('respuesta', 'N/A')[:100]}...")
                print(f"   🎯 Confianza: {respuesta.get('confianza', 0):.2f}")
            
            if len(qa_resultados) > 3:
                print(f"\n   ... y {len(qa_resultados) - 3} respuestas más")
            
            return {
                "success": True,
                "filename": filename,
                "responses_count": len(qa_resultados),
                "latency_ms": metadatos.get('latencia_ms', 0),
                "model": metadatos.get('modelo', 'N/A')
            }
            
        else:
            error = result.get("error", {}) if isinstance(result, dict) else {}
            print(f"❌ Error: {error.get('codigo', 'UNKNOWN')}")
            print(f"   Detalle: {error.get('detalle', 'Sin detalles')}")
            
            return {
                "success": False,
                "filename": filename,
                "error": error.get('codigo', 'UNKNOWN'),
                "detail": error.get('detalle', 'Sin detalles')
            }
            
    except Exception as e:
        print(f"💥 Excepción: {str(e)}")
        return {
            "success": False,
            "filename": filename,
            "error": "EXCEPTION",
            "detail": str(e)
        }


def main():
    """Función principal"""
    print("🧪 Testing QA Service con Archivos de Contratos")
    print("=" * 60)
    
    # Verificar API key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  OPENAI_API_KEY no encontrada")
        print("   Configura tu API key:")
        print("   export OPENAI_API_KEY=sk-your-key-here")
        print("\n📝 Continuando solo con validaciones...")
    else:
        print(f"✅ OPENAI_API_KEY encontrada: {api_key[:10]}...")
    
    # Obtener archivos de contratos
    contract_files = get_contract_files()
    
    if not contract_files:
        print(f"\n📁 No se encontraron archivos .txt en la carpeta contratos/")
        print("   Sube algunos archivos de texto con contratos para probar")
        return 1
    
    print(f"\n📋 Archivos encontrados: {len(contract_files)}")
    for file_path in contract_files:
        filename = os.path.basename(file_path)
        print(f"   📄 {filename}")
    
    # Crear preguntas de prueba
    questions = create_test_questions()
    print(f"\n❓ Preguntas de prueba: {len(questions)}")
    
    # Procesar cada archivo
    results = []
    for file_path in contract_files:
        filename = os.path.basename(file_path)
        
        # Leer archivo
        contract_text = read_contract_file(file_path)
        
        if not contract_text:
            print(f"⚠️  Saltando {filename} (archivo vacío o error)")
            continue
        
        if len(contract_text) < 100:
            print(f"⚠️  Saltando {filename} (muy corto: {len(contract_text)} chars)")
            continue
        
        # Procesar contrato
        result = test_single_contract(contract_text, filename, questions)
        results.append(result)
        
        # Pausa entre archivos
        if len(contract_files) > 1:
            print("\n" + "="*30)
    
    # Resumen final
    print(f"\n📊 RESUMEN FINAL")
    print("=" * 60)
    
    successful = [r for r in results if r.get("success")]
    failed = [r for r in results if not r.get("success")]
    
    print(f"✅ Exitosos: {len(successful)}")
    print(f"❌ Fallidos: {len(failed)}")
    
    if successful:
        avg_latency = sum(r.get("latency_ms", 0) for r in successful) / len(successful)
        print(f"⏱️  Latencia promedio: {avg_latency:.0f} ms")
        
        models_used = set(r.get("model", 'N/A') for r in successful)
        print(f"🤖 Modelos usados: {', '.join(models_used)}")
    
    if failed:
        print(f"\n❌ Errores encontrados:")
        for result in failed:
            print(f"   📄 {result.get('filename', 'N/A')}: {result.get('error', 'N/A')}")
    
    print(f"\n🎉 Testing completado!")
    return 0 if len(failed) == 0 else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
