#!/bin/bash
# Script para iniciar el proyecto completo

echo "🚀 Iniciando Parchís Distribuido..."
echo ""

PROJECT_ROOT="/home/saantigh/Universidad/sistemas_distribuidos/Parques"

# Limpiar procesos anteriores primero
echo "🧹 Limpiando procesos anteriores..."
bash "$PROJECT_ROOT/CLEAN.sh"
echo ""

echo "📝 Instrucciones:"
echo "   1. Este script abrirá 2 terminales"
echo "   2. Terminal 1: Backend (Node.js)"
echo "   3. Terminal 2: Frontend (Vite)"
echo ""
echo "⌨️  Para detener los servidores: Ctrl+C en cada terminal"
echo ""

# Verificar que gnome-terminal esté disponible
if command -v gnome-terminal &> /dev/null; then
    echo "✅ Usando gnome-terminal"
    
    # Terminal para Backend
    gnome-terminal --title="Backend - Parchís" -- bash -c "
        cd $PROJECT_ROOT/backend
        echo '═══════════════════════════════════════'
        echo '🔧 BACKEND - Node.js + Express'
        echo '═══════════════════════════════════════'
        echo ''
        echo '📍 Puerto: 3001'
        echo '🔗 URL: http://localhost:3001'
        echo ''
        npm run dev
        echo ''
        echo '⚠️  Servidor detenido. Presiona Enter para cerrar...'
        read
    "
    
    sleep 1
    
    # Terminal para Frontend
    gnome-terminal --title="Frontend - Parchís" -- bash -c "
        cd $PROJECT_ROOT/frontend
        echo '═══════════════════════════════════════'
        echo '🎨 FRONTEND - Vite + React'
        echo '═══════════════════════════════════════'
        echo ''
        echo '📍 Puerto: 5173 (probablemente)'
        echo '🔗 URL: Se mostrará abajo'
        echo ''
        npm run dev
        echo ''
        echo '⚠️  Servidor detenido. Presiona Enter para cerrar...'
        read
    "
    
    echo "✅ Terminales abiertas"
    echo "🌐 Accede al juego en: http://localhost:5173"
    
elif command -v x-terminal-emulator &> /dev/null; then
    echo "✅ Usando x-terminal-emulator"
    
    x-terminal-emulator -e "bash -c 'cd $PROJECT_ROOT/backend && echo Backend && npm run dev; read'" &
    x-terminal-emulator -e "bash -c 'cd $PROJECT_ROOT/frontend && echo Frontend && npm run dev; read'" &
    
else
    echo "⚠️  No se detectó terminal gráfica"
    echo ""
    echo "📋 Ejecuta manualmente:"
    echo ""
    echo "Terminal 1:"
    echo "  cd $PROJECT_ROOT/backend"
    echo "  npm run dev"
    echo ""
    echo "Terminal 2:"
    echo "  cd $PROJECT_ROOT/frontend"
    echo "  npm run dev"
fi
