# Análisis del Repositorio binder-text-extract y Plan de Desarrollo

## 📋 Resumen del Análisis

He analizado completamente el repositorio `binder-text-extract` y he identificado los patrones arquitectónicos clave para reutilizar en el nuevo proyecto.

## 🏗️ Arquitectura Identificada

### 1. **Punto de Entrada (lambda_function.py)**
- **Handler principal**: Maneja eventos HTTP y directos
- **Detección automática**: Distingue entre API Gateway y invocación directa
- **CORS**: Soporte completo para preflight requests
- **Logging estructurado**: Con contexto de request ID y métricas
- **Manejo de errores**: Robusto con logging de excepciones

### 2. **Configuración AWS (aws_clients.py)**
```python
# Patrón identificado:
def make_boto_clients(region: str):
    cfg = Config(
        region_name=region,
        read_timeout=25,
        connect_timeout=5,
        retries={"max_attempts": 3, "mode": "standard"},
        max_pool_connections=10,
    )
    session = boto3.session.Session(region_name=region)
    s3 = session.client("s3", config=cfg)
    textract = session.client("textract", config=cfg)
    lambda_client = session.client("lambda", config=cfg)
    return s3, textract, lambda_client
```

**Elementos clave a reutilizar:**
- Configuración de timeouts y reintentos
- Manejo de sesiones boto3
- Retorno de múltiples clientes AWS

### 3. **Sistema de Configuración (config.py)**
```python
@dataclass(frozen=True)
class AppConfig:
    default_bucket: str
    region: str
    allowed_origin: str
    # ... otros campos
```

**Patrón identificado:**
- Uso de dataclasses inmutables
- Configuración centralizada con defaults
- Soporte para variables de entorno

### 4. **Arquitectura LLM (carpeta call_llm/)**

#### **Estructura Modular:**
- `api.py`: Punto de entrada principal
- `openai_service.py`: Servicio OpenAI con múltiples estrategias
- `http.py`: Cliente HTTP personalizado
- `schemas.py`: Definición de esquemas JSON
- `env.py`: Manejo de variables de entorno
- `prompt.py`: Gestión de prompts

#### **Patrón de Llamadas OpenAI Identificado:**

1. **Configuración Flexible:**
```python
@dataclass
class OpenAIConfig:
    model: str = "gpt-5-nano"
    reasoning_effort: Optional[str] = "low"
    timeout: int = 45
    max_output_tokens: int = 32768
    fallback_model: str = "gpt-4o-mini"
```

2. **Múltiples Estrategias de Fallback:**
   - **Primary**: Responses API con schema JSON estricto
   - **Fallback 1**: Chat completions con JSON strict
   - **Fallback 2**: Chat completions sin formato estricto
   - **Fallback 3**: Modelo alternativo (gpt-4o-mini)

3. **Manejo Robusto de Errores:**
   - Detección de errores específicos (reasoning no soportado, schema inválido, contexto muy largo)
   - Reintentos automáticos con ajustes
   - Logging detallado de errores

4. **Validación y Normalización:**
```python
def normalize_structured_output(data: Any) -> Dict[str, Any]:
    # Normaliza el JSON devuelto por el LLM a la forma esperada
    # Convierte tipos y asegura estructura consistente
```

## 📋 Análisis del Brief - QA Personalizado

### **Requisitos Identificados:**

1. **Función Lambda síncrona** para procesar preguntas personalizadas sobre contratos
2. **Entrada JSON** con texto del contrato y array de preguntas
3. **Salida estructurada** con respuestas ordenadas y metadatos
4. **Webhook opcional** para notificaciones asíncronas
5. **Validaciones específicas** (máx. 50 preguntas, 300 chars por pregunta)
6. **Manejo de errores** con códigos específicos
7. **Logging y métricas** en CloudWatch

### **Diferencias Clave vs. binder-text-extract:**
- **Síncrono vs. Asíncrono**: Este proyecto es síncrono, el original es asíncrono con worker
- **QA específico vs. Extracción general**: Enfoque en preguntas personalizadas
- **Estructura de salida diferente**: Array de QA vs. JSON estructurado fijo
- **Sin Textract**: No necesita OCR, solo procesamiento de texto

## 🎯 Plan de Desarrollo Específico

### **Fase 1: Estructura Base del Proyecto QA**
- [ ] Crear estructura de proyecto `binder-qa-personalizado`
- [ ] Implementar `lambda_function.py` adaptado para QA síncrono
- [ ] Configurar `aws_clients.py` (solo para logging, sin S3/Textract)
- [ ] Crear `config.py` con configuración específica QA
- [ ] Implementar `qa_service/` con lógica específica

### **Fase 2: Adaptación del Sistema LLM**
- [ ] Reutilizar carpeta `call_llm/` como base
- [ ] Crear `qa_schemas.py` para validación de entrada/salida QA
- [ ] Adaptar `openai_service.py` para procesamiento de preguntas múltiples
- [ ] Crear `qa_prompt.txt` específico para QA sobre contratos
- [ ] Implementar `qa_parser.py` para procesar respuestas estructuradas

### **Fase 3: Lógica de Negocio QA**
- [ ] Implementar `qa_controller.py` con flujo síncrono
- [ ] Crear `qa_validator.py` con validaciones específicas
- [ ] Implementar `qa_processor.py` para manejo de múltiples preguntas
- [ ] Crear `webhook_service.py` para notificaciones opcionales
- [ ] Implementar sistema de confianza y razonamiento

### **Fase 4: Validaciones y Manejo de Errores**
- [ ] Validación de entrada (máx. 50 preguntas, 300 chars)
- [ ] Validación de webhook URL (HTTPS, dominios permitidos)
- [ ] Manejo de timeouts (30-120s)
- [ ] Códigos de error específicos (BAD_REQUEST, TIMEOUT, MODEL_ERROR, WEBHOOK_ERROR)
- [ ] Sistema de reintentos para webhooks con backoff exponencial

### **Fase 5: Testing y Deployment**
- [ ] Configurar testing local con casos de QA
- [ ] Validar integración con OpenAI
- [ ] Configurar API Gateway
- [ ] Configurar CloudWatch logs y métricas
- [ ] Documentación y ejemplos de uso

## 🔧 Componentes a Reutilizar Directamente

### **1. Sistema LLM Completo**
- ✅ **Carpeta `call_llm/` completa** - Arquitectura robusta y probada
- ✅ **Múltiples estrategias de fallback** - Garantiza alta disponibilidad
- ✅ **Manejo de errores específicos** - Experiencia probada en producción

### **2. Configuración AWS**
- ✅ **`aws_clients.py`** - Patrón de configuración optimizado
- ✅ **Configuración de timeouts y reintentos** - Valores probados
- ✅ **Manejo de sesiones boto3** - Mejores prácticas

### **3. Infraestructura HTTP**
- ✅ **`http_gateway.py`** - Soporte completo para API Gateway
- ✅ **Manejo de CORS** - Configuración robusta
- ✅ **Parsing de eventos** - Soporte para múltiples formatos

### **4. Sistema de Logging**
- ✅ **Logging estructurado** - Con contexto y métricas
- ✅ **Manejo de request IDs** - Para trazabilidad
- ✅ **Eventos semánticos** - Fácil debugging

## 📝 Notas Importantes

1. **El repositorio analizado está muy bien estructurado** con separación clara de responsabilidades
2. **El sistema LLM es especialmente robusto** con múltiples estrategias de fallback
3. **La configuración AWS sigue mejores prácticas** con timeouts y reintentos apropiados
4. **El manejo de errores es exhaustivo** con logging detallado

## 🔧 Especificaciones Técnicas Detalladas

### **Estructura de Archivos Propuesta:**
```
binder-qa-personalizado/
├── lambda_function.py
├── qa_service/
│   ├── __init__.py
│   ├── controller.py
│   ├── validator.py
│   ├── processor.py
│   ├── webhook_service.py
│   └── schemas.py
├── call_llm/
│   ├── __init__.py
│   ├── api.py
│   ├── openai_service.py
│   ├── qa_schemas.py
│   ├── qa_parser.py
│   ├── http.py
│   ├── env.py
│   └── prompt.py
├── config.py
├── aws_clients.py
├── http_gateway.py
├── logging.py
├── utils.py
└── qa_prompt.txt
```

### **Adaptaciones Específicas del Sistema LLM:**

#### **1. qa_schemas.py** (Nuevo)
```python
def qa_input_schema() -> Dict:
    """Schema para validar entrada de QA"""
    return {
        "type": "object",
        "properties": {
            "texto_contrato": {"type": "string", "minLength": 1},
            "reference_id": {"type": "string", "minLength": 1},
            "qa": {
                "type": "object",
                "properties": {
                    "webhook_url": {"type": "string", "format": "uri"},
                    "incluir_razonamiento": {"type": "boolean"},
                    "preguntas": {
                        "type": "array",
                        "items": {"type": "string", "maxLength": 300},
                        "maxItems": 50,
                        "minItems": 1
                    }
                },
                "required": ["preguntas"]
            }
        },
        "required": ["texto_contrato", "reference_id", "qa"]
    }

def qa_output_schema() -> Dict:
    """Schema para estructura de salida QA"""
    return {
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "reference_id": {"type": "string"},
            "qa_resultados": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "pregunta_orden": {"type": "integer"},
                        "pregunta": {"type": "string"},
                        "respuesta": {"type": "string"},
                        "confianza": {"type": "number", "minimum": 0, "maximum": 1},
                        "razonamiento": {"type": "string"}
                    }
                }
            },
            "metadatos": {
                "type": "object",
                "properties": {
                    "modelo": {"type": "string"},
                    "latencia_ms": {"type": "integer"},
                    "modo": {"type": "string"},
                    "webhook_disparado": {"type": "boolean"}
                }
            }
        }
    }
```

#### **2. qa_prompt.txt** (Nuevo)
```text
Eres un experto en análisis de contratos y documentos legales.

TAREA: Analizar el contrato proporcionado y responder las preguntas específicas de manera precisa y estructurada.

INSTRUCCIONES:
1. Lee cuidadosamente todo el texto del contrato
2. Para cada pregunta, busca la información relevante en el contrato
3. Proporciona respuestas claras y específicas
4. Si no encuentras información, responde "No se encontró información en el contrato"
5. Incluye nivel de confianza (0.0 a 1.0) basado en la claridad de la información
6. Si se solicita razonamiento, explica brevemente dónde encontraste la información

FORMATO DE RESPUESTA:
- Cada respuesta debe ser un objeto JSON con: pregunta_orden, pregunta, respuesta, confianza, razonamiento
- Las respuestas deben mantener el mismo orden que las preguntas de entrada
- Usa confianza alta (0.8-1.0) para información explícita y clara
- Usa confianza media (0.5-0.7) para información inferida o parcial
- Usa confianza baja (0.1-0.4) para información incierta o ambigua

CONTRATO:
{texto_contrato}

PREGUNTAS:
{preguntas_formateadas}
```

#### **3. qa_processor.py** (Nuevo)
```python
class QAProcessor:
    """Procesador de preguntas y respuestas personalizadas"""
    
    def __init__(self, openai_service, config):
        self.openai_service = openai_service
        self.config = config
    
    def process_questions(self, texto_contrato: str, preguntas: List[str], 
                         incluir_razonamiento: bool = False) -> List[Dict]:
        """Procesa múltiples preguntas sobre un contrato"""
        # Formatear preguntas para el prompt
        preguntas_formateadas = self._format_questions(preguntas)
        
        # Llamar a OpenAI con prompt específico
        respuestas_raw = self.openai_service.run_qa(
            texto_contrato=texto_contrato,
            preguntas=preguntas_formateadas,
            incluir_razonamiento=incluir_razonamiento
        )
        
        # Procesar y normalizar respuestas
        return self._normalize_responses(respuestas_raw, preguntas)
```

### **Configuración Específica:**

#### **config.py** (Adaptado)
```python
@dataclass(frozen=True)
class QAConfig:
    # Límites de validación
    max_preguntas: int = 50
    max_chars_pregunta: int = 300
    min_chars_contrato: int = 100
    
    # Timeouts
    openai_timeout: int = 60
    webhook_timeout: int = 30
    max_total_timeout: int = 120
    
    # OpenAI
    default_model: str = "gpt-4o-mini"
    fallback_model: str = "gpt-3.5-turbo"
    max_output_tokens: int = 4096
    
    # Webhook
    webhook_retry_attempts: int = 3
    webhook_backoff_base: float = 1.5
    
    # AWS
    region: str = "us-east-1"
    log_level: str = "INFO"
```

## 🚀 Próximos Pasos

1. **Crear estructura del proyecto** con los archivos identificados
2. **Implementar validaciones** específicas del brief
3. **Adaptar sistema LLM** para QA personalizado
4. **Implementar controller** con flujo síncrono
5. **Configurar webhook service** para notificaciones opcionales

---

*El plan está completo y listo para implementación. ¿Quieres que proceda con la creación de la estructura del proyecto?*
