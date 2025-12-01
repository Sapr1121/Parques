#!/bin/bash
# Script de instalación y configuración del proyecto Parchís

echo "═══════════════════════════════════════════════════════════════"
echo "🎮 INSTALACIÓN Y CONFIGURACIÓN - PARCHÍS DISTRIBUIDO 🎮"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Directorio base del proyecto
PROJECT_ROOT="/home/saantigh/Universidad/sistemas_distribuidos/Parques"

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}📍 Directorio del proyecto: ${PROJECT_ROOT}${NC}"
echo ""

# ============================================
# 1. VERIFICAR NODE Y NPM
# ============================================
echo -e "${YELLOW}[1/6]${NC} Verificando Node.js y npm..."

if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js no está instalado${NC}"
    echo "Instala Node.js desde: https://nodejs.org/"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm no está instalado${NC}"
    exit 1
fi

NODE_VERSION=$(node --version)
NPM_VERSION=$(npm --version)
echo -e "${GREEN}✅ Node.js: ${NODE_VERSION}${NC}"
echo -e "${GREEN}✅ npm: ${NPM_VERSION}${NC}"
echo ""

# ============================================
# 2. VERIFICAR PYTHON
# ============================================
echo -e "${YELLOW}[2/6]${NC} Verificando Python..."

if [ -f "${PROJECT_ROOT}/pythonserver/venv/bin/python3" ]; then
    PYTHON_CMD="${PROJECT_ROOT}/pythonserver/venv/bin/python3"
    PYTHON_VERSION=$($PYTHON_CMD --version)
    echo -e "${GREEN}✅ Python (venv): ${PYTHON_VERSION}${NC}"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    PYTHON_VERSION=$(python3 --version)
    echo -e "${YELLOW}⚠️  Python (sistema): ${PYTHON_VERSION}${NC}"
    echo -e "${YELLOW}   Recomendado: Crear entorno virtual en pythonserver/venv${NC}"
else
    echo -e "${RED}❌ Python3 no está instalado${NC}"
    exit 1
fi
echo ""

# ============================================
# 3. VERIFICAR ARCHIVOS .env
# ============================================
echo -e "${YELLOW}[3/6]${NC} Verificando archivos .env..."

if [ -f "${PROJECT_ROOT}/frontend/.env" ]; then
    echo -e "${GREEN}✅ frontend/.env existe${NC}"
    cat "${PROJECT_ROOT}/frontend/.env" | head -3
else
    echo -e "${RED}❌ frontend/.env NO existe${NC}"
    echo "   Creando archivo..."
    echo "VITE_BACKEND_URL=http://localhost:3001" > "${PROJECT_ROOT}/frontend/.env"
    echo -e "${GREEN}✅ Creado${NC}"
fi

echo ""

if [ -f "${PROJECT_ROOT}/backend/.env" ]; then
    echo -e "${GREEN}✅ backend/.env existe${NC}"
    cat "${PROJECT_ROOT}/backend/.env" | head -5
else
    echo -e "${RED}❌ backend/.env NO existe${NC}"
    exit 1
fi
echo ""

# ============================================
# 4. INSTALAR DEPENDENCIAS DE BACKEND
# ============================================
echo -e "${YELLOW}[4/6]${NC} Instalando dependencias del BACKEND..."
cd "${PROJECT_ROOT}/backend" || exit 1

if [ -d "node_modules" ]; then
    echo -e "${BLUE}ℹ️  node_modules ya existe, actualizando...${NC}"
fi

npm install

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Dependencias de backend instaladas${NC}"
else
    echo -e "${RED}❌ Error instalando dependencias de backend${NC}"
    exit 1
fi
echo ""

# ============================================
# 5. INSTALAR DEPENDENCIAS DE FRONTEND
# ============================================
echo -e "${YELLOW}[5/6]${NC} Instalando dependencias del FRONTEND..."
cd "${PROJECT_ROOT}/frontend" || exit 1

if [ -d "node_modules" ]; then
    echo -e "${BLUE}ℹ️  node_modules ya existe, actualizando...${NC}"
fi

npm install

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Dependencias de frontend instaladas${NC}"
else
    echo -e "${RED}❌ Error instalando dependencias de frontend${NC}"
    exit 1
fi
echo ""

# ============================================
# 6. VERIFICAR DEPENDENCIAS DE PYTHON
# ============================================
echo -e "${YELLOW}[6/6]${NC} Verificando dependencias de Python..."

if [ -f "${PROJECT_ROOT}/requirements.txt" ]; then
    echo -e "${BLUE}ℹ️  Archivo requirements.txt encontrado${NC}"
    
    if [ -f "${PROJECT_ROOT}/pythonserver/venv/bin/pip" ]; then
        echo "Instalando dependencias de Python en el entorno virtual..."
        "${PROJECT_ROOT}/pythonserver/venv/bin/pip" install -r "${PROJECT_ROOT}/requirements.txt"
        echo -e "${GREEN}✅ Dependencias de Python instaladas${NC}"
    else
        echo -e "${YELLOW}⚠️  No hay entorno virtual, omitiendo instalación de Python${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  No se encontró requirements.txt${NC}"
fi
echo ""

# ============================================
# RESUMEN FINAL
# ============================================
echo "═══════════════════════════════════════════════════════════════"
echo -e "${GREEN}✨ INSTALACIÓN COMPLETADA ✨${NC}"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo -e "${BLUE}📝 SIGUIENTE PASO:${NC} Iniciar los servidores"
echo ""
echo -e "${YELLOW}Terminal 1 - Backend:${NC}"
echo "  cd ${PROJECT_ROOT}/backend"
echo "  npm run dev"
echo ""
echo -e "${YELLOW}Terminal 2 - Frontend:${NC}"
echo "  cd ${PROJECT_ROOT}/frontend"
echo "  npm run dev"
echo ""
echo -e "${BLUE}🌐 URLs esperadas:${NC}"
echo "  • Frontend: http://localhost:5173"
echo "  • Backend: http://localhost:3001"
echo "  • Python Server: ws://localhost:8001"
echo "  • Registry: tcp://localhost:9000"
echo ""
echo "═══════════════════════════════════════════════════════════════"
