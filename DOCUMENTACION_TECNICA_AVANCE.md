# 📋 Documentación Técnica de Avance - BinderUtilsPreguntasPersonalizadas

## 🎯 Resumen Ejecutivo

El proyecto **BinderUtilsPreguntasPersonalizadas** ha sido desarrollado exitosamente como un servicio Lambda de AWS para procesar preguntas personalizadas sobre contratos y documentos. El desarrollo siguió una metodología de desarrollo local primero, seguida de migración a AWS Lambda, y actualmente está integrado con Bubble.io.

---

## 🏗️ 1. Desarrollo Local

### 1.1 Arquitectura Base Reutilizada

El proyecto se desarrolló tomando como base la arquitectura probada del repositorio `binder-text-extract`, reutilizando los siguientes componentes:

#### **Componentes Adaptados:**
- **Sistema LLM** (`call_llm/`): Adaptado para manejo de preguntas personalizadas
  - `api.py`: Cliente HTTP para OpenAI con fallback automático
  - `openai_service.py`: Servicio principal de OpenAI
  - `qa_parser.py`: Parser robusto de respuestas JSON
  - `qa_schemas.py`: Esquemas de validación de entrada y salida
  - `prompt.py`: Gestión de prompts especializados para QA

- **Infraestructura AWS** (`aws_clients.py`, `http_gateway.py`):
  - Configuración optimizada de boto3
  - Manejo de eventos HTTP (API Gateway y invocación directa)
  - Sistema de logging estructurado para CloudWatch

- **Configuración Centralizada** (`config.py`):
  - Variables de entorno con valores por defecto
  - Configuración flexible para diferentes entornos

### 1.2 Librerías y Configuraciones Adaptadas

#### **Dependencias Principales:**
```python
# requirements.txt
boto3>=1.26.0          # Cliente AWS (solo para logging)
openai>=1.0.0           # Cliente OpenAI
requests>=2.28.0        # Cliente HTTP personalizado
```

#### **Configuraciones Específicas:**
- **Modelos OpenAI**: GPT-4o-mini (principal) → GPT-3.5-turbo (fallback)
- **Límites de Validación**: 
  - Máximo 50 preguntas por request
  - Máximo 300 caracteres por pregunta
  - Mínimo 100 caracteres en contrato
- **Timeout**: 30-120 segundos configurable
- **Webhooks**: Soporte opcional con reintentos exponenciales

### 1.3 Testing Local Implementado

#### **Tests de Estructura** (`local/test_structure.py`):
- ✅ Validación de imports y dependencias
- ✅ Configuración de variables de entorno
- ✅ Validación de esquemas JSON
- ✅ Parser de respuestas OpenAI
- ✅ HTTP Gateway (eventos directos y API Gateway)

#### **Tests Funcionales** (`local/test_local.py`):
- ✅ Contrato de ejemplo con 5 preguntas
- ✅ Validación completa del flujo end-to-end
- ✅ Manejo de errores y respuestas estructuradas
- ✅ Logging detallado para debugging

#### **Ejemplo de Uso** (`example_usage.py`):
- ✅ Contrato realista de 18 meses
- ✅ 8 preguntas variadas de diferentes tipos
- ✅ Demostración de capacidades del sistema
- ✅ Manejo de errores y casos edge

---

## 🚀 2. Migración a AWS Lambda

### 2.1 Proceso de Despliegue

#### **Script de Despliegue Automatizado** (`deploy.sh`):
```bash
# Configuración Lambda
FUNCTION_NAME="qa-personalizado"
REGION="us-east-1"
RUNTIME="python3.9"
HANDLER="lambda_function.lambda_handler"
TIMEOUT=180
MEMORY_SIZE=1024
```

#### **Proceso de Despliegue:**
1. **Preparación del Paquete**: Copia de archivos necesarios, exclusión de archivos de desarrollo
2. **Instalación de Dependencias**: Instalación automática de requirements.txt
3. **Creación de ZIP**: Archivo optimizado para Lambda
4. **Despliegue AWS**: Creación o actualización de función Lambda
5. **Configuración**: Variables de entorno automáticas desde `.env`

### 2.2 Variables de Entorno Configuradas

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-proj-your-openai-api-key-here
OPENAI_MODEL=gpt-5-nano
OPENAI_FALLBACK_MODEL=gpt-4o-mini
OPENAI_MAX_OUTPUT_TOKENS=32768
OPENAI_TIMEOUT=45

# QA Configuration
QA_MAX_PREGUNTAS=50
QA_MAX_CHARS_PREGUNTA=300
QA_MIN_CHARS_CONTRATO=100

# Webhook Configuration
WEBHOOK_TIMEOUT=30
WEBHOOK_RETRY_ATTEMPTS=3
WEBHOOK_BACKOFF_BASE=1.5

# AWS Configuration
AWS_REGION=us-east-1
LOG_LEVEL=INFO
ALLOWED_ORIGIN=*
```

### 2.3 Estructura del Endpoint

#### **API Gateway Configurado:**
- **API ID**: `y4sl1ajasl`
- **Nombre**: `qa-personalizado-api`
- **Stage**: `prod`
- **URL**: `https://y4sl1ajasl.execute-api.us-east-1.amazonaws.com/prod`
- **Método**: POST
- **Integración**: AWS_PROXY con Lambda
- **CORS**: Habilitado para frontend

#### **Handler Lambda** (`lambda_function.py`):
- Manejo síncrono de requests
- Soporte para API Gateway y invocación directa
- CORS configurado automáticamente
- Logging estructurado para CloudWatch
- Manejo de errores robusto

### 2.4 Manejo de IDs de Preguntas

#### **Esquema de Entrada:**
```json
{
  "texto_contrato": "<texto del contrato>",
  "reference_id": "req-001",
  "qa": {
    "preguntas": [
      "[OBJ001] ¿Cuál es el objeto del contrato?",
      "[PAR002] ¿Quiénes son las partes involucradas?",
      "[MON003] ¿Cuál es el monto del contrato?"
    ]
  }
}
```

#### **Procesamiento de IDs:**
- **Extracción**: El parser identifica IDs en formato `[ID]` al inicio de preguntas
- **Trazabilidad**: Los IDs se mantienen en la respuesta para asociación posterior
- **Validación**: IDs únicos por request, formato alfanumérico

#### **Esquema de Salida:**
```json
{
  "success": true,
  "reference_id": "req-001",
  "qa_resultados": [
    {
      "id": "OBJ001",
      "pregunta_orden": 1,
      "pregunta": "¿Cuál es el objeto del contrato?",
      "respuesta": "Prestación de servicios de consultoría...",
      "confianza": 0.95,
      "razonamiento": "Identificado en la cláusula primera"
    }
  ]
}
```

---

## 🔗 3. Estado Actual en Bubble

### 3.1 Integración Implementada

#### **API Connector Configurado:**
- **Endpoint**: `https://y4sl1ajasl.execute-api.us-east-1.amazonaws.com/prod`
- **Método**: POST
- **Autenticación**: Sin autenticación (público)
- **Headers**: Content-Type: application/json
- **CORS**: Habilitado para dominio Bubble

#### **Workflow "Binder Utils Preguntas Personalizadas":**
- **Trigger**: Manual o desde otro workflow
- **Input**: 
  - `texto_contrato`: Texto del contrato a analizar
  - `reference_id`: ID único para trazabilidad
  - `preguntas`: Array de preguntas con formato `[ID] pregunta`
- **Output**: Respuesta estructurada con resultados de QA

### 3.2 Funcionalidades Operativas

#### **✅ Implementado:**
- Conexión exitosa con Lambda function
- Envío de preguntas individuales con IDs
- Recepción de respuestas estructuradas
- Manejo de errores y códigos de estado
- Logging de requests y responses

#### **✅ Validaciones Activas:**
- Máximo 50 preguntas por request
- Máximo 300 caracteres por pregunta
- Formato de ID válido `[ID]`
- Texto de contrato mínimo 100 caracteres

### 3.3 Pendientes por Implementar

#### **🔄 En Progreso:**
1. **Pasar arreglo completo de preguntas por parámetro**
   - Actualmente se envían preguntas individuales
   - Necesario: Envío de array completo en un solo request
   - Beneficio: Mayor eficiencia y consistencia

2. **Desarrollar guardado/asociación al ASIM correspondiente**
   - Implementar lógica de guardado en base de datos
   - Asociar respuestas con el ASIM (Asesoramiento Integral)
   - Crear relaciones entre preguntas y documentos
   - Implementar historial de consultas

#### **📋 Especificaciones Técnicas Pendientes:**

**Para Array Completo de Preguntas:**
```json
{
  "texto_contrato": "<texto>",
  "reference_id": "ASIM-2024-001",
  "qa": {
    "preguntas": [
      "[OBJ001] ¿Cuál es el objeto del contrato?",
      "[PAR002] ¿Quiénes son las partes?",
      "[MON003] ¿Cuál es el monto?",
      "[VIG004] ¿Cuál es la vigencia?",
      "[CON005] ¿Existe cláusula de confidencialidad?"
    ],
    "incluir_razonamiento": true
  }
}
```

**Para Guardado/Asociación ASIM:**
- Crear tabla `qa_responses` en Bubble
- Campos: `asim_id`, `reference_id`, `pregunta_id`, `respuesta`, `confianza`, `timestamp`
- Implementar workflow de guardado post-respuesta
- Crear relaciones con documentos y usuarios

---

## 📊 4. Métricas y Monitoreo

### 4.1 CloudWatch Logs

#### **Log Group**: `/aws/lambda/qa-personalizado`
- **Formato**: Text estructurado
- **Retención**: Por defecto (sin expiración)
- **Eventos Loggeados**:
  - `qa.start`: Inicio de procesamiento
  - `qa.success`: Procesamiento exitoso
  - `qa.error`: Errores en procesamiento
  - `webhook.dispatched`: Envío de webhooks

### 4.2 Métricas Disponibles

- **Invocaciones totales**
- **Duración de ejecución** (promedio: ~1.3 segundos)
- **Errores y códigos de estado**
- **Throttles y concurrent executions**
- **Uso de memoria** (configurado: 1024 MB)

### 4.3 Costos y Optimización

#### **Costos Actuales:**
- **Lambda**: ~$0.0000166667 por GB-segundo
- **OpenAI**: ~$0.00015 por 1K tokens (GPT-5 nano)
- **API Gateway**: $3.50 por millón de requests

#### **Optimizaciones Implementadas:**
- Fallback automático a modelos más económicos
- Timeout configurable para evitar costos innecesarios
- Logging estructurado para debugging eficiente
- Reutilización de conexiones HTTP

---

## 🎯 5. Próximos Pasos Recomendados

### 5.1 Corto Plazo (1-2 semanas)

1. **Implementar envío de array completo de preguntas**
   - Modificar workflow Bubble para enviar todas las preguntas
   - Validar respuesta con múltiples resultados
   - Probar con casos edge (máximo 50 preguntas)

2. **Desarrollar sistema de guardado ASIM**
   - Diseñar esquema de base de datos
   - Implementar workflow de guardado
   - Crear relaciones con documentos existentes

### 5.2 Mediano Plazo (1 mes)

3. **Implementar historial de consultas**
   - Vista de consultas anteriores por ASIM
   - Filtros por fecha, tipo de documento, usuario
   - Exportación de resultados

4. **Optimizar rendimiento**
   - Implementar cache de respuestas frecuentes
   - Optimizar prompts para reducir tokens
   - Monitorear costos y ajustar límites

### 5.3 Largo Plazo (2-3 meses)

5. **Funcionalidades avanzadas**
   - Análisis de tendencias en consultas
   - Sugerencias automáticas de preguntas
   - Integración con otros servicios Binder

6. **Escalabilidad**
   - Implementar rate limiting
   - Configurar auto-scaling
   - Optimizar para alto volumen

---

## 📋 6. Resumen de Estado

### ✅ **Completado (100%)**
- Desarrollo local con arquitectura robusta
- Migración exitosa a AWS Lambda
- Endpoint API Gateway funcional
- Integración básica con Bubble
- Sistema de IDs para trazabilidad
- Validaciones y manejo de errores
- Logging y monitoreo completo

### 🔄 **En Progreso (70%)**
- Integración completa con Bubble workflows
- Optimización de envío de preguntas múltiples

### ⏳ **Pendiente (30%)**
- Sistema de guardado/asociación ASIM
- Historial de consultas
- Funcionalidades avanzadas de análisis

---

## 🔧 7. Información Técnica de Contacto

### **Recursos AWS:**
- **Lambda Function**: `qa-personalizado`
- **API Gateway**: `y4sl1ajasl`
- **Region**: `us-east-1`
- **Endpoint**: `https://y4sl1ajasl.execute-api.us-east-1.amazonaws.com/prod`

### **Documentación Adicional:**
- **README Principal**: `binder-qa-personalizado/README.md`
- **Resumen Ejecutivo**: `RESUMEN_EJECUTIVO.md`
- **Deploy Success**: `binder-qa-personalizado/DEPLOY_SUCCESS.md`

### **Scripts de Utilidad:**
- **Deploy**: `binder-qa-personalizado/deploy.sh`
- **Test Local**: `binder-qa-personalizado/local/test_local.py`
- **Ejemplo de Uso**: `binder-qa-personalizado/example_usage.py`

---

**📅 Última actualización**: 23 de Septiembre, 2025  
**👨‍💻 Estado del proyecto**: En producción, funcional, con integración Bubble en progreso  
**🎯 Próximo milestone**: Implementación completa de guardado ASIM
