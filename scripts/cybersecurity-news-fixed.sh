#!/bin/bash

# Script mejorado con logging y prevención de duplicados

LOG_FILE="/tmp/cybersecurity-news.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

echo "=== Ejecución $TIMESTAMP ===" >> "$LOG_FILE"

# Ejecutar script Python mejorado
python3 /Users/jmaudisio/.openclaw/workspace/scripts/cybersecurity-news-fixed.py 2>&1 | tee -a "$LOG_FILE"

EXIT_CODE=${PIPESTATUS[0]}

echo "Código de salida: $EXIT_CODE" >> "$LOG_FILE"
echo "=== Fin ejecución ===" >> "$LOG_FILE" >> "$LOG_FILE"

exit $EXIT_CODE