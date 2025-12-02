#!/bin/bash
# Script para limpiar procesos Python que puedan estar corriendo

echo "🧹 Limpiando procesos anteriores..."

# Buscar procesos en puertos específicos
PORTS=(8001 9000)
KILLED=0

for PORT in "${PORTS[@]}"; do
    PID=$(lsof -ti :$PORT 2>/dev/null)
    if [ ! -z "$PID" ]; then
        echo "  🔴 Puerto $PORT ocupado por PID $PID"
        kill $PID 2>/dev/null && echo "  ✅ Proceso $PID detenido" && KILLED=$((KILLED+1))
    fi
done

if [ $KILLED -eq 0 ]; then
    echo "  ✨ No había procesos activos"
else
    echo "  ✅ $KILLED proceso(s) detenido(s)"
fi

echo ""
echo "🎯 Puertos liberados. Listo para iniciar."
