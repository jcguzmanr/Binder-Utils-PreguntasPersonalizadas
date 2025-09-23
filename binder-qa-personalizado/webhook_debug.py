#!/usr/bin/env python3
"""
Script de diagnóstico para problemas de webhook
"""

import json
import sys
import os
from typing import Dict, Any

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from qa_service.webhook_service import WebhookService
from config import default_config
from app_logging import get_app_logger


def test_webhook_url(webhook_url: str, test_payload: Dict[str, Any] = None) -> None:
    """Prueba una URL de webhook con un payload de prueba"""
    
    if test_payload is None:
        test_payload = {
            "success": True,
            "reference_id": "test-debug-123",
            "qa_resultados": [
                {
                    "pregunta": "¿Cuál es el objeto del contrato?",
                    "respuesta": "El objeto del contrato es la prestación de servicios de consultoría.",
                    "confianza": 0.95,
                    "razonamiento": "Esta información se encuentra claramente establecida en la cláusula primera del contrato."
                }
            ],
            "metadatos": {
                "modelo": "gpt-4o-mini",
                "latencia_ms": 1500,
                "modo": "debug",
                "webhook_disparado": False
            }
        }
    
    # Configurar logger
    logger = get_app_logger(json_logs=True, level="DEBUG")
    config = default_config()
    
    # Crear servicio de webhook
    webhook_service = WebhookService(config, logger)
    
    print(f"🔍 Probando webhook: {webhook_url}")
    print(f"📦 Payload size: {len(json.dumps(test_payload))} bytes")
    print(f"⏱️  Timeout: {config.webhook_timeout}s")
    print(f"🔄 Reintentos: {config.webhook_retry_attempts}")
    print(f"📈 Backoff base: {config.webhook_backoff_base}")
    print(f"🔒 HTTPS requerido: {config.require_https_webhook}")
    print(f"🌐 Dominios permitidos: {config.allowed_webhook_domains}")
    print("-" * 50)
    
    # Probar validación de URL
    is_valid, validation_error = webhook_service._validate_webhook_url(webhook_url)
    if not is_valid:
        print(f"❌ Validación de URL falló: {validation_error}")
        return
    
    print("✅ Validación de URL exitosa")
    
    # Probar envío síncrono
    print("\n🔄 Probando envío síncrono...")
    success, error = webhook_service.send_webhook(webhook_url, test_payload)
    
    if success:
        print("✅ Webhook enviado exitosamente")
    else:
        print(f"❌ Webhook falló: {error}")
    
    # Probar envío asíncrono
    print("\n🚀 Probando envío asíncrono...")
    try:
        webhook_service.send_webhook_async(webhook_url, test_payload)
        print("✅ Webhook asíncrono despachado")
    except Exception as e:
        print(f"❌ Webhook asíncrono falló: {e}")


def main():
    """Función principal"""
    if len(sys.argv) < 2:
        print("Uso: python webhook_debug.py <webhook_url>")
        print("Ejemplo: python webhook_debug.py https://webhook.site/12345678-1234-1234-1234-123456789012")
        sys.exit(1)
    
    webhook_url = sys.argv[1]
    test_webhook_url(webhook_url)


if __name__ == "__main__":
    main()
