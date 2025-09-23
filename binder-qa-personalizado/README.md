# QA Personalizado Service

Servicio Lambda para procesar preguntas personalizadas sobre contratos/documentos y devolver respuestas en formato estructurado.

## 🚀 Características

- ✅ **Procesamiento síncrono** de preguntas personalizadas sobre contratos
- ✅ **Integración con OpenAI** usando modelos GPT-4o-mini y GPT-3.5-turbo
- ✅ **Respuestas estructuradas** con nivel de confianza y razonamiento opcional
- ✅ **Webhooks opcionales** para notificaciones asíncronas
- ✅ **Validaciones robustas** con límites configurables
- ✅ **Manejo de errores** con códigos específicos
- ✅ **Logging estructurado** para CloudWatch
- ✅ **Python puro** sin dependencias externas pesadas

## 📁 Estructura del Proyecto

```
binder-qa-personalizado/
├── lambda_function.py          # Handler principal de Lambda
├── config.py                   # Configuración centralizada
├── logging.py                  # Sistema de logging estructurado
├── aws_clients.py             # Clientes AWS (solo logging)
├── http_gateway.py            # Manejo de eventos HTTP
├── qa_service/                # Servicios específicos de QA
│   ├── controller.py          # Controller principal
│   ├── validator.py           # Validaciones de entrada
│   └── webhook_service.py     # Servicio de webhooks
├── call_llm/                  # Sistema LLM adaptado
│   ├── api.py                 # API principal para OpenAI
│   ├── openai_service.py      # Servicio OpenAI
│   ├── qa_parser.py           # Parser de respuestas
│   ├── qa_schemas.py          # Schemas de validación
│   ├── prompt.py              # Gestión de prompts
│   └── http.py                # Cliente HTTP personalizado
├── local/                     # Testing local
│   └── test_local.py          # Script de pruebas
├── qa_prompt.txt              # Prompt específico para QA
├── requirements.txt           # Dependencias
└── env.example                # Variables de entorno ejemplo
```

## 🛠️ Configuración

### 1. Variables de Entorno

Copia `env.example` a `.env` y configura:

```bash
cp env.example .env
```

Variables principales:
- `OPENAI_API_KEY`: Tu API key de OpenAI (requerido)
- `OPENAI_MODEL`: Modelo principal (default: gpt-4o-mini)
- `QA_MAX_PREGUNTAS`: Máximo de preguntas (default: 50)
- `QA_MAX_CHARS_PREGUNTA`: Máximo caracteres por pregunta (default: 300)

### 2. Instalación Local

```bash
# Clonar o descargar el proyecto
cd binder-qa-personalizado

# Instalar dependencias (opcional para desarrollo)
pip install -r requirements.txt

# Configurar variables de entorno
cp env.example .env
# Editar .env con tu API key
```

## 🧪 Testing Local

```bash
# Ejecutar test local
python local/test_local.py
```

El script incluye:
- Contrato de ejemplo
- 5 preguntas de prueba
- Validación completa del flujo
- Logging detallado

## 📡 API

### Entrada

```json
{
  "texto_contrato": "<texto íntegro del contrato>",
  "reference_id": "<string>",
  "qa": {
    "webhook_url": "https://dominio.com/webhook",
    "incluir_razonamiento": false,
    "preguntas": [
      "¿Cuál es el monto de la remuneración mensual?",
      "¿Cuál es la fecha de inicio del contrato?",
      "¿Existe cláusula de confidencialidad?"
    ]
  }
}
```

### Salida Exitosa

```json
{
  "success": true,
  "reference_id": "req-001",
  "qa_resultados": [
    {
      "pregunta_orden": 1,
      "pregunta": "¿Cuál es el monto de la remuneración mensual?",
      "respuesta": "S/ 5,000.00 mensuales",
      "confianza": 0.86,
      "razonamiento": "Identificado en la cláusula de remuneración."
    }
  ],
  "metadatos": {
    "modelo": "gpt-4o-mini",
    "latencia_ms": 1280,
    "modo": "sync",
    "webhook_disparado": true
  }
}
```

### Salida de Error

```json
{
  "success": false,
  "reference_id": "req-001",
  "error": {
    "codigo": "BAD_REQUEST",
    "detalle": "Maximum 50 preguntas allowed"
  }
}
```

## 🔧 Despliegue en AWS

### 1. Crear Paquete de Despliegue

```bash
# Crear zip para Lambda
zip -r qa-personalizado.zip . -x "*.git*" "*.pyc" "__pycache__/*" "local/*" ".env*"
```

### 2. Configurar Lambda

- **Runtime**: Python 3.9+
- **Handler**: `lambda_function.lambda_handler`
- **Timeout**: 2-3 minutos
- **Memory**: 512MB-1GB

### 3. Variables de Entorno en Lambda

```bash
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
QA_MAX_PREGUNTAS=50
LOG_LEVEL=INFO
```

### 4. API Gateway

- Crear REST API
- Configurar CORS
- Mapear a Lambda function
- Habilitar CloudWatch logs

## 📊 Monitoreo

### Logs Estructurados

```json
{
  "timestamp": "2024-01-15T10:30:00.000Z",
  "level": "INFO",
  "event": "qa.start",
  "id": "req-001",
  "preguntas_count": 3,
  "incluir_razonamiento": true
}
```

### Métricas CloudWatch

- Duración de ejecución
- Tasa de éxito/error
- Uso de memoria
- Invocaciones

## 🔒 Seguridad

- Validación de entrada robusta
- Límites configurables
- Soporte para dominios webhook permitidos
- HTTPS requerido para webhooks (opcional)

## 🚨 Límites y Validaciones

- **Máximo 50 preguntas** por request
- **Máximo 300 caracteres** por pregunta
- **Mínimo 100 caracteres** en contrato
- **Timeout 30-120 segundos**
- **Webhook URL** debe ser HTTPS (configurable)

## 🔄 Códigos de Error

- `BAD_REQUEST`: Error en validación de entrada
- `TIMEOUT`: Timeout en OpenAI o webhook
- `MODEL_ERROR`: Error en procesamiento de OpenAI
- `WEBHOOK_ERROR`: Error en envío de webhook

## 📝 Notas de Desarrollo

- **Python puro**: Sin dependencias externas pesadas
- **Reutilización**: Basado en arquitectura probada de binder-text-extract
- **Fallback automático**: Cambio automático entre modelos OpenAI
- **Logging detallado**: Para debugging y monitoreo
- **Testing local**: Script completo de pruebas

## 🤝 Contribución

1. Fork el proyecto
2. Crear feature branch
3. Hacer cambios
4. Ejecutar tests locales
5. Crear pull request

## 🔧 Diagnóstico de Webhooks

Si tienes problemas con webhooks que no llegan, usa el script de diagnóstico:

```bash
# Probar una URL de webhook
python webhook_debug.py https://webhook.site/12345678-1234-1234-1234-123456789012

# El script probará:
# - Validación de URL
# - Envío síncrono
# - Envío asíncrono
# - Configuración actual
```

### Problemas Comunes de Webhooks

1. **URL inválida**: Verifica que la URL sea HTTP/HTTPS válida
2. **Timeout**: Aumenta `WEBHOOK_TIMEOUT` si el servidor es lento
3. **HTTPS requerido**: Configura `REQUIRE_HTTPS_WEBHOOK=true`
4. **Dominios bloqueados**: Configura `ALLOWED_WEBHOOK_DOMAINS`
5. **Modo asíncrono**: Usa `WEBHOOK_ASYNC_MODE=true` para no esperar respuesta

### Logs de CloudWatch

Busca estos eventos en los logs:
- `webhook.validation_failed`: URL inválida
- `webhook.attempt`: Intento de envío
- `webhook.response`: Respuesta del servidor
- `webhook.timeout`: Timeout en envío
- `webhook.http_error`: Error HTTP específico
- `webhook.async_dispatched`: Webhook asíncrono despachado

## 📄 Licencia

[Especificar licencia según necesidades]
