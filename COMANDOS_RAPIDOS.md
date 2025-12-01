# 🎮 Parchís Distribuido - Comandos Rápidos

## 🚀 Inicio Rápido

```bash
# Limpiar procesos anteriores e iniciar todo
bash START.sh
```

## 🧹 Limpiar Procesos

Si tienes el error "Address already in use":

```bash
bash CLEAN.sh
```

## 🔧 Comandos Individuales

### Backend
```bash
cd backend
npm run dev
```

### Frontend
```bash
cd frontend
npm run dev
```

## 🌐 URLs

- **Frontend:** http://localhost:5173
- **Backend:** http://localhost:3001
- **Python Server:** ws://localhost:8001
- **Registry:** tcp://localhost:9000

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
bash START.sh
```

---

📖 **Guía completa:** Ver `GUIA_INSTALACION.md`
