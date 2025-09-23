#!/bin/bash

# Script de despliegue para AWS Lambda
# QA Personalizado Service

set -e

echo "🚀 Desplegando QA Personalizado Service a AWS Lambda"
echo "=================================================="

# Configuración
FUNCTION_NAME="qa-personalizado"
REGION="us-east-1"
RUNTIME="python3.9"
HANDLER="lambda_function.lambda_handler"
TIMEOUT=180
MEMORY_SIZE=1024

# Verificar que estamos en el directorio correcto
if [ ! -f "lambda_function.py" ]; then
    echo "❌ Error: No se encuentra lambda_function.py"
    echo "   Ejecuta este script desde el directorio del proyecto"
    exit 1
fi

# Crear directorio temporal para el paquete
TEMP_DIR=$(mktemp -d)
echo "📁 Directorio temporal: $TEMP_DIR"

# Copiar archivos necesarios
echo "📦 Preparando paquete de despliegue..."
cp lambda_function.py "$TEMP_DIR/"
cp -r qa_service/ "$TEMP_DIR/"
cp -r call_llm/ "$TEMP_DIR/"
cp config.py "$TEMP_DIR/"
cp app_logging.py "$TEMP_DIR/"
cp aws_clients.py "$TEMP_DIR/"
cp http_gateway.py "$TEMP_DIR/"
cp utils.py "$TEMP_DIR/"
cp qa_prompt.txt "$TEMP_DIR/"

# Crear archivo de dependencias si no existe
if [ ! -f "requirements.txt" ] || [ ! -s "requirements.txt" ]; then
    echo "# Dependencias mínimas para AWS Lambda" > "$TEMP_DIR/requirements.txt"
    echo "boto3>=1.26.0" >> "$TEMP_DIR/requirements.txt"
fi

# Instalar dependencias en el directorio temporal
echo "📚 Instalando dependencias..."
cd "$TEMP_DIR"
pip install -r requirements.txt -t .

# Crear archivo ZIP
ZIP_FILE="qa-personalizado-$(date +%Y%m%d-%H%M%S).zip"
echo "🗜️  Creando archivo ZIP: $ZIP_FILE"
zip -r "$ZIP_FILE" . -x "*.pyc" "__pycache__/*" "*.git*" "local/*" "*.md" "*.sh" "env.example" ".env*"

# Verificar que AWS CLI está configurado
if ! command -v aws &> /dev/null; then
    echo "❌ Error: AWS CLI no está instalado o no está en PATH"
    echo "   Instala AWS CLI: https://aws.amazon.com/cli/"
    exit 1
fi

# Verificar credenciales AWS
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ Error: AWS CLI no está configurado correctamente"
    echo "   Ejecuta: aws configure"
    exit 1
fi

echo "✅ AWS CLI configurado correctamente"

# Verificar si la función existe
if aws lambda get-function --function-name "$FUNCTION_NAME" --region "$REGION" &> /dev/null; then
    echo "🔄 Función Lambda existente encontrada, actualizando..."
    
    # Actualizar código
    aws lambda update-function-code \
        --function-name "$FUNCTION_NAME" \
        --zip-file "fileb://$ZIP_FILE" \
        --region "$REGION"
    
    # Actualizar configuración
    aws lambda update-function-configuration \
        --function-name "$FUNCTION_NAME" \
        --runtime "$RUNTIME" \
        --handler "$HANDLER" \
        --timeout "$TIMEOUT" \
        --memory-size "$MEMORY_SIZE" \
        --region "$REGION"
    
    echo "✅ Función Lambda actualizada exitosamente"
    
else
    echo "🆕 Creando nueva función Lambda..."
    
    # Crear función Lambda
    aws lambda create-function \
        --function-name "$FUNCTION_NAME" \
        --runtime "$RUNTIME" \
        --role "arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):role/lambda-execution-role" \
        --handler "$HANDLER" \
        --zip-file "fileb://$ZIP_FILE" \
        --timeout "$TIMEOUT" \
        --memory-size "$MEMORY_SIZE" \
        --region "$REGION"
    
    echo "✅ Función Lambda creada exitosamente"
fi

# Configurar variables de entorno (si existe archivo .env)
if [ -f ".env" ]; then
    echo "🔧 Configurando variables de entorno desde .env..."
    
    # Extraer variables de entorno del archivo .env
    ENV_VARS=""
    while IFS='=' read -r key value; do
        # Ignorar comentarios y líneas vacías
        if [[ ! "$key" =~ ^[[:space:]]*# ]] && [[ -n "$key" ]]; then
            # Remover comillas si las hay
            value=$(echo "$value" | sed 's/^"\(.*\)"$/\1/' | sed "s/^'\(.*\)'$/\1/")
            ENV_VARS="$ENV_VARS $key=$value"
        fi
    done < .env
    
    if [ -n "$ENV_VARS" ]; then
        aws lambda update-function-configuration \
            --function-name "$FUNCTION_NAME" \
            --environment "Variables={$ENV_VARS}" \
            --region "$REGION"
        
        echo "✅ Variables de entorno configuradas"
    fi
else
    echo "⚠️  No se encontró archivo .env"
    echo "   Configura las variables de entorno manualmente en AWS Console"
fi

# Limpiar archivo temporal
cd - > /dev/null
rm -rf "$TEMP_DIR"

echo ""
echo "🎉 Despliegue completado exitosamente!"
echo ""
echo "📋 Información de la función:"
echo "   Nombre: $FUNCTION_NAME"
echo "   Región: $REGION"
echo "   Runtime: $RUNTIME"
echo "   Handler: $HANDLER"
echo "   Timeout: $TIMEOUT segundos"
echo "   Memoria: $MEMORY_SIZE MB"
echo ""
echo "🔗 URLs útiles:"
echo "   AWS Console: https://console.aws.amazon.com/lambda/home?region=$REGION#/functions/$FUNCTION_NAME"
echo "   API Gateway: https://console.aws.amazon.com/apigateway/home?region=$REGION"
echo ""
echo "📝 Próximos pasos:"
echo "1. Configurar API Gateway para exponer la función"
echo "2. Configurar variables de entorno si no se hizo automáticamente"
echo "3. Probar la función con el evento de ejemplo"
echo "4. Configurar CloudWatch logs para monitoreo"
