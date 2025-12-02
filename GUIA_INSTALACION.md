# 🎮 Parchís Distribuido - Guía de Instalación y Uso

## 📦 Requisitos Previos

- **Node.js** v18 o superior (actualmente: v24.7.0 ✅)
- **npm** v9 o superior (actualmente: v11.6.0 ✅)
- **Python** 3.11+ (actualmente: 3.13.7 ✅)

---

## 🚀 Instalación Rápida

### Opción 1: Script Automático (Recomendado)

```bash
cd /home/saantigh/Universidad/sistemas_distribuidos/Parques
bash SETUP.sh
```

Este script:
- ✅ Verifica Node.js, npm y Python
- ✅ Crea archivos `.env` si no existen
- ✅ Instala dependencias de backend
- ✅ Instala dependencias de frontend
- ✅ Verifica dependencias de Python

### Opción 2: Manual

1. **Instalar dependencias del Backend**
```bash
cd backend
npm install
```

2. **Instalar dependencias del Frontend**
```bash
cd frontend
npm install
```

---

## ⚙️ Configuración

Ya se crearon los archivos `.env` necesarios:

### `frontend/.env`
```env
VITE_BACKEND_URL=http://localhost:3001
```

### `backend/.env`
```env
PORT=3001
PYTHON_ROOT=../pythonserver
PYTHON_SERVER_PORT=8001
REGISTRY_PORT=9000
PYTHON_CMD=../pythonserver/venv/bin/python3
```

---

## 🎯 Iniciar el Proyecto

### Opción 1: Script Automático

```bash
bash START.sh
```

Esto abrirá 2 terminales automáticamente:
- 🔧 Backend (Node.js) en `http://localhost:3001`
- 🎨 Frontend (Vite) en `http://localhost:5173`

### Opción 2: Manual (2 Terminales)

**Terminal 1 - Backend:**
```bash
cd backend
npm run dev
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

---

## 🌐 URLs del Sistema

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **Frontend** | http://localhost:5173 | Interfaz de usuario (React + Vite) |
| **Backend** | http://localhost:3001 | API REST (Node.js + Express) |
| **Python Game Server** | ws://localhost:8001 | Servidor WebSocket del juego |
| **Registry Server** | tcp://localhost:9000 | Servidor de registro de salas |

---

## 🎮 Cómo Jugar

1. **Abrir el navegador** en `http://localhost:5173`
2. **Crear una sala:**
   - Ingresa tu nombre
   - Elige tu color
   - Haz clic en "Crear Sala"
   - Comparte el **código de 8 caracteres** con otros jugadores
3. **Unirse a una sala:**
   - Ingresa el código de sala
   - Ingresa tu nombre
   - Haz clic en "Unirse"

---

## 🏗️ Estructura del Proyecto

```
Parques/
├── frontend/          # React + TypeScript + Vite
│   ├── src/
│   ├── package.json
│   └── .env
├── backend/           # Node.js + Express + TypeScript
│   ├── src/
│   ├── package.json
│   └── .env
├── pythonserver/      # Servidor de juego Python + WebSocket
│   ├── server/
│   ├── client/
│   └── game/
├── SETUP.sh          # Script de instalación
└── START.sh          # Script de inicio rápido
```

---

## 🐛 Solución de Problemas

### ⚠️ Error: "Address already in use" (Puerto ocupado)

Si ves este error:
```
OSError: [Errno 98] address already in use
```

**Solución rápida:**
```bash
bash CLEAN.sh
```

Este script limpia automáticamente los procesos Python que puedan estar corriendo en los puertos 8001 y 9000.

**Solución manual:**
```bash
# Ver qué procesos están usando los puertos
lsof -i :8001
lsof -i :9000

# Detener el proceso (usa el PID que te muestre el comando anterior)
kill <PID>
```

### El backend no inicia

```bash
cd backend
rm -rf node_modules
npm install
npm run dev
```

### El frontend no inicia

```bash
cd frontend
rm -rf node_modules
npm install
npm run dev
```

### Puerto ya en uso

Si el puerto 3001 o 5173 están ocupados:

**Backend:**
```bash
# Editar backend/.env
PORT=3002  # Cambiar a otro puerto
```

**Frontend:** Vite te sugerirá automáticamente otro puerto.

### Error de CORS

Verifica que `VITE_BACKEND_URL` en `frontend/.env` apunte a la URL correcta del backend.

---

## 📝 Notas Importantes

- ⚠️ **Firewall:** Asegúrate de que los puertos 3001, 5173, 8001 y 9000 estén abiertos
- 🌐 **Red Local:** Para jugar desde otros dispositivos, usa la IP local en lugar de `localhost`
- 🔄 **Hot Reload:** Los cambios en el código se reflejan automáticamente (tanto frontend como backend)

---

## ✅ Estado de la Instalación

- ✅ Node.js v24.7.0
- ✅ npm v11.6.0
- ✅ Python 3.13.7 (venv)
- ✅ Dependencias de backend instaladas
- ✅ Dependencias de frontend instaladas
- ✅ Archivos `.env` configurados

---

## 📞 Soporte

Si encuentras problemas, verifica:
1. Que todos los servicios estén corriendo
2. Los logs en las terminales de backend y frontend
3. La consola del navegador (F12) para errores de frontend

---

¡Disfruta el juego! 🎲🎉
