# Apple Health - Análisis de Entrenamientos

## Estado: Pendiente de Jose

## Objetivo
Analizar datos de salud de Jose para ayudarle con entrenamientos

## Opciones exploradas

### Opción 1: Export manual desde iPhone
- Salud → Perfil → Exportar datos
- Genera ZIP con export.xml
- Convertir a CSV para análisis

### Opción 2: App Health Auto Export
- Descargar en iPhone
- Exporta directamente a CSV
- Más limpio que el método nativo

### Opción 3: MCP Apple Health (skill instalada)
- Requiere: @neiltron/apple-health-mcp
- Necesita: HEALTH_DATA_DIR con CSVs
- Permite consultas SQL

## Datos que podemos analizar
- Pasos diarios
- Sueño
- Ejercicios/Entrenamientos
- Ritmo cardíaco
- Progreso semanal/mensual

## Siguiente paso
Jose va a pensar cómo proceder. Necesita exportar sus datos de salud desde el iPhone.

## Notas
- Skill apple-health instalada en ~/.openclaw/workspace/skills/apple-health/
- MCP requiere Node.js configurado
- Alternativa simple: exportar CSV y进行分析
