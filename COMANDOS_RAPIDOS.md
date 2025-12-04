# 🎮 Parchís Distribuido - Comandos Rápidos

## 🚀 Inicio Rápido (Modo Red - Multijugador)

```bash
# Iniciar todo con soporte para múltiples máquinas en red
cd /home/valentina/Parques
./START_RED.sh
```

Este script:
- Detecta tu IP automáticamente
- Limpia puertos ocupados
- Configura el frontend con tu IP
- Inicia backend y frontend

## 🧹 Limpiar Procesos

Si tienes el error "Address already in use":

```bash
bash CLEAN.sh
```

O manualmente:
```bash
sudo fuser -k 8001/tcp 3001/tcp 5173/tcp 9000/tcp
```

## 🔧 Comandos Individuales

### Backend (Terminal 1)
```bash
cd /home/valentina/Parques/backend
npm run dev
```

### Frontend (Terminal 2)
```bash
cd /home/valentina/Parques/frontend
npm run dev
```

## 🌐 URLs

### Modo Local (misma máquina)
- **Frontend:** http://localhost:5173
- **Backend:** http://localhost:3001
- **Python Server:** ws://localhost:8001
- **Registry:** tcp://localhost:9000

### Modo Red (otras máquinas)
```bash
# Obtener tu IP
hostname -I
```
- **Frontend:** http://[TU_IP]:5173
- **WebSocket:** ws://[TU_IP]:8001

Ejemplo: Si tu IP es `192.168.1.19`:
- Otros jugadores abren: `http://192.168.1.19:5173`

## 🛑 Detener Todo

En cada terminal donde estén corriendo servicios:
```
Ctrl + C
```

## 📋 Verificar Puertos

```bash
# Ver procesos en puertos específicos
lsof -i :3001  # Backend
lsof -i :5173  # Frontend
lsof -i :8001  # Python Server
lsof -i :9000  # Registry

# Detener un proceso específico
kill <PID>
```

## 🆘 En Caso de Emergencia

```bash
# Detener TODOS los procesos Node.js y Python
pkill -9 node
pkill -9 python3

# Luego reinicia con:
./START_RED.sh
```

## 🎲 Cómo Jugar en Red

1. **Máquina Servidor** ejecuta `./START_RED.sh`
2. **Otras máquinas** abren navegador → `http://[IP_SERVIDOR]:5173`
3. Un jugador **Crea Sala** → obtiene código
4. Otros jugadores **Se Unen** con el código
5. ¡A jugar! 🎮

---

📖 **Guía completa de red:** Ver `GUIA_RED_MULTIMAQUINA.md`
