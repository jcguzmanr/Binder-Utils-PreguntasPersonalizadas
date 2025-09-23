#!/usr/bin/env python3
"""
Ejemplo de uso del servicio QA personalizado
"""

import json
import sys
from pathlib import Path

# Agregar directorio al path para imports
sys.path.insert(0, str(Path(__file__).parent))

from lambda_function import lambda_handler


def example_contract_analysis():
    """Ejemplo de análisis de contrato"""
    
    # Evento de ejemplo
    event = {
        "texto_contrato": """
        CONTRATO DE PRESTACIÓN DE SERVICIOS DE CONSULTORÍA
        
        CONTRATO DE PRESTACIÓN DE SERVICIOS que celebran por una parte, 
        EMPRESA TECNOLÓGICA S.A.C., con RUC 20123456789, con domicilio 
        en Av. Principal 123, Lima, representada por su Gerente General 
        Carlos Mendoza Silva, identificado con DNI 12345678, a quien en 
        adelante se le denominará "EL CONTRATANTE"; y por otra parte, 
        JUAN CARLOS PÉREZ GARCÍA, identificado con DNI 87654321, con 
        domicilio en Jr. Comercial 456, Lima, a quien en adelante se 
        le denominará "EL CONSULTOR", bajo las siguientes cláusulas:
        
        PRIMERA: OBJETO DEL CONTRATO
        El objeto del presente contrato es la prestación de servicios 
        de consultoría en transformación digital, análisis de procesos 
        empresariales y optimización de sistemas de información por 
        parte del CONSULTOR a favor del CONTRATANTE.
        
        SEGUNDA: OBLIGACIONES DEL CONSULTOR
        2.1. Desarrollar un diagnóstico completo de los procesos actuales
        2.2. Proponer mejoras en los sistemas de información
        2.3. Capacitar al personal en las nuevas tecnologías
        2.4. Entregar informes mensuales de avance
        
        TERCERA: REMUNERACIÓN
        Por los servicios prestados, el CONTRATANTE pagará al CONSULTOR 
        la suma de S/ 8,500.00 (ocho mil quinientos soles) mensuales, 
        los cuales serán cancelados hasta el día 5 de cada mes siguiente 
        al mes trabajado, mediante transferencia bancaria a la cuenta 
        del CONSULTOR.
        
        CUARTA: VIGENCIA
        El presente contrato tendrá una duración de 18 (dieciocho) meses, 
        contados a partir del 1 de marzo de 2024, pudiendo ser renovado 
        por períodos iguales de mutuo acuerdo entre las partes, previa 
        evaluación del cumplimiento de objetivos.
        
        QUINTA: CONFIDENCIALIDAD
        Las partes se comprometen a mantener la más estricta confidencialidad 
        sobre toda la información que se intercambie en virtud del presente 
        contrato, incluyendo datos de clientes, estrategias comerciales, 
        procesos internos y cualquier información sensible de la empresa.
        
        SEXTA: TERMINACIÓN
        El presente contrato podrá ser terminado anticipadamente por 
        cualquiera de las partes con un preaviso de 30 días calendario, 
        sin responsabilidad adicional, salvo el pago de las obligaciones 
        pendientes hasta la fecha de terminación.
        
        SÉPTIMA: FIRMAS
        En señal de conformidad, se firma el presente contrato en Lima, 
        a los 20 días del mes de febrero de 2024.
        
        EL CONTRATANTE                          EL CONSULTOR
        EMPRESA TECNOLÓGICA S.A.C.             JUAN CARLOS PÉREZ GARCÍA
        Carlos Mendoza Silva                   DNI: 87654321
        DNI: 12345678
        """,
        "reference_id": "CONTRATO-2024-001",
        "qa": {
            "incluir_razonamiento": True,
            "preguntas": [
                "¿Cuál es el monto de la remuneración mensual?",
                "¿Cuál es la fecha de inicio del contrato?",
                "¿Cuál es la duración del contrato?",
                "¿Existe cláusula de confidencialidad?",
                "¿Quién es el consultor?",
                "¿Cuál es el objeto del contrato?",
                "¿Cuándo se pagan los honorarios?",
                "¿Se puede terminar anticipadamente el contrato?"
            ]
        }
    }
    
    # Contexto mock
    class MockContext:
        def __init__(self):
            self.function_name = "qa-personalizado-example"
    
    context = MockContext()
    
    print("📋 Ejemplo de Análisis de Contrato")
    print("=" * 50)
    print(f"📄 Contrato: {len(event['texto_contrato'])} caracteres")
    print(f"❓ Preguntas: {len(event['qa']['preguntas'])}")
    print(f"🆔 Reference ID: {event['reference_id']}")
    print()
    
    try:
        # Ejecutar análisis
        print("🚀 Ejecutando análisis...")
        result = lambda_handler(event, context)
        
        # Mostrar resultado
        if isinstance(result, dict):
            if result.get("success"):
                print("✅ Análisis exitoso!")
                print()
                
                # Mostrar metadatos
                metadatos = result.get("metadatos", {})
                print("📊 Metadatos:")
                print(f"   Modelo: {metadatos.get('modelo', 'N/A')}")
                print(f"   Latencia: {metadatos.get('latencia_ms', 'N/A')} ms")
                print(f"   Modo: {metadatos.get('modo', 'N/A')}")
                print(f"   Webhook: {metadatos.get('webhook_disparado', False)}")
                print()
                
                # Mostrar respuestas
                qa_resultados = result.get("qa_resultados", [])
                print("💬 Respuestas:")
                for i, respuesta in enumerate(qa_resultados, 1):
                    print(f"\n{i}. {respuesta.get('pregunta', 'N/A')}")
                    print(f"   📝 Respuesta: {respuesta.get('respuesta', 'N/A')}")
                    print(f"   🎯 Confianza: {respuesta.get('confianza', 'N/A'):.2f}")
                    if respuesta.get('razonamiento'):
                        print(f"   💭 Razonamiento: {respuesta.get('razonamiento', 'N/A')}")
                
                print(f"\n🎉 Análisis completado con {len(qa_resultados)} respuestas")
                
            else:
                print("❌ Análisis falló")
                error = result.get("error", {})
                print(f"   Código: {error.get('codigo', 'N/A')}")
                print(f"   Detalle: {error.get('detalle', 'N/A')}")
        
        else:
            print("❌ Respuesta inesperada")
            print(f"   Tipo: {type(result)}")
            print(f"   Contenido: {result}")
            
    except Exception as e:
        print(f"💥 Error durante la ejecución: {str(e)}")
        import traceback
        traceback.print_exc()


def example_error_handling():
    """Ejemplo de manejo de errores"""
    
    print("\n" + "=" * 50)
    print("🚨 Ejemplo de Manejo de Errores")
    print("=" * 50)
    
    # Evento con error (texto muy corto)
    invalid_event = {
        "texto_contrato": "Muy corto",
        "reference_id": "ERROR-001",
        "qa": {
            "preguntas": ["¿Qué pasa aquí?"]
        }
    }
    
    class MockContext:
        def __init__(self):
            self.function_name = "qa-personalizado-error"
    
    context = MockContext()
    
    try:
        result = lambda_handler(invalid_event, context)
        
        if isinstance(result, dict) and not result.get("success"):
            print("✅ Error capturado correctamente:")
            error = result.get("error", {})
            print(f"   Código: {error.get('codigo', 'N/A')}")
            print(f"   Detalle: {error.get('detalle', 'N/A')}")
        else:
            print("❌ Error no fue capturado como esperado")
            
    except Exception as e:
        print(f"💥 Excepción inesperada: {str(e)}")


def main():
    """Función principal"""
    print("🧪 Ejemplos de Uso - QA Personalizado Service")
    print("=" * 60)
    
    # Verificar API key
    import os
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  OPENAI_API_KEY no encontrada")
        print("   Para probar con OpenAI, configura tu API key:")
        print("   export OPENAI_API_KEY=sk-your-key-here")
        print("\n📝 Ejecutando ejemplo sin API key (solo validaciones)...")
        print()
    else:
        print(f"✅ OPENAI_API_KEY encontrada: {api_key[:10]}...")
        print()
    
    # Ejecutar ejemplos
    example_contract_analysis()
    example_error_handling()
    
    print("\n" + "=" * 60)
    print("📚 Para más información, consulta README.md")


if __name__ == "__main__":
    main()
