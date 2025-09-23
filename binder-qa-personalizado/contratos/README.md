# 📁 Carpeta de Contratos para Testing

Esta carpeta está destinada a contener archivos de texto (.txt) con contratos para probar el sistema de QA personalizado.

## 📋 Cómo usar:

1. **Sube archivos .txt** con contratos en esta carpeta
2. **Ejecuta el script de prueba** que leerá automáticamente los archivos
3. **El sistema procesará** cada contrato con preguntas de ejemplo

## 📝 Formato esperado:

- **Archivos .txt** con texto plano
- **Contenido:** Contratos, documentos legales, acuerdos, etc.
- **Encoding:** UTF-8 recomendado

## 🧪 Scripts disponibles:

- `../local/test_with_files.py` - Prueba con archivos de esta carpeta
- `../example_usage.py` - Ejemplo con contrato hardcodeado
- `../local/test_structure.py` - Test de estructura del sistema

## 📊 Ejemplo de uso:

```bash
# Desde el directorio binder-qa-personalizado
python3 local/test_with_files.py
```

El script automáticamente:
1. Buscará archivos .txt en esta carpeta
2. Los procesará uno por uno
3. Aplicará preguntas de ejemplo
4. Mostrará los resultados
