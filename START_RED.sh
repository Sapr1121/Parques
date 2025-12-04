#!/bin/bash

# ============================================
# Script para iniciar Parqués en modo RED
# ============================================

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║           🎮 PARQUÉS - MODO MULTIJUGADOR EN RED            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Obtener IP de la máquina
IP=$(hostname -I | awk '{print $1}')

if [ -z "$IP" ]; then
    IP="localhost"
    echo -e "${YELLOW}⚠️  No se pudo detectar la IP. Usando localhost${NC}"
fi

echo -e "${GREEN}📡 IP del servidor detectada: ${YELLOW}$IP${NC}"
echo ""

# Matar procesos anteriores en los puertos
echo -e "${YELLOW}🧹 Limpiando puertos...${NC}"
fuser -k 8001/tcp 2>/dev/null
fuser -k 3001/tcp 2>/dev/null
fuser -k 5173/tcp 2>/dev/null
fuser -k 9000/tcp 2>/dev/null
sleep 1

# Mostrar instrucciones
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}📋 INSTRUCCIONES PARA LA DEMOSTRACIÓN:${NC}"
echo ""
echo -e "   ${YELLOW}1. SERVIDOR (esta máquina):${NC}"
echo -e "      Frontend: ${GREEN}http://$IP:5173${NC}"
echo ""
echo -e "   ${YELLOW}2. CLIENTES (otras máquinas):${NC}"
echo -e "      Abrir navegador e ir a: ${GREEN}http://$IP:5173${NC}"
echo ""
echo -e "   ${YELLOW}3. Para jugar:${NC}"
echo -e "      - Un jugador crea sala"
echo -e "      - Los demás se unen con el código"
echo -e "      - ¡A jugar!"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

# Preguntar si continuar
read -p "¿Iniciar servidores? (s/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo -e "${RED}Cancelado.${NC}"
    exit 0
fi

# Crear archivo .env temporal con la IP correcta
echo -e "${YELLOW}⚙️  Configurando frontend con IP: $IP${NC}"
cat > frontend/.env << EOF
VITE_WS_URL=ws://$IP:8001
VITE_API_URL=http://$IP:3001
EOF

# Iniciar Backend en segundo plano
echo -e "${GREEN}🚀 Iniciando Backend...${NC}"
cd backend
npm run dev &
BACKEND_PID=$!
cd ..

# Esperar a que el backend inicie
sleep 3

# Iniciar Frontend
echo -e "${GREEN}🚀 Iniciando Frontend...${NC}"
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo -e "${GREEN}✅ Servidores iniciados!${NC}"
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "   ${GREEN}🌐 ACCESO DESDE OTRAS MÁQUINAS:${NC}"
echo -e "   ${YELLOW}   http://$IP:5173${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}Presiona Ctrl+C para detener los servidores${NC}"
echo ""

# Esperar a que el usuario presione Ctrl+C
trap "echo -e '\n${RED}Deteniendo servidores...${NC}'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT

# Mantener el script corriendo
wait
