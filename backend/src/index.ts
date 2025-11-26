import express from 'express';
import cors from 'cors';
import 'dotenv/config';
import roomRoutes from './routes/roomRoutes';
import { launchPythonServers, killPythonServers } from './services/pythonService';

const app = express();
app.use(cors());
app.use(express.json());

app.use('/api', roomRoutes);

const PORT = process.env.PORT ?? 3001;

app.listen(PORT, () => {
  console.log(`✅ API Node+TS lista en http://localhost:${PORT}`);
  
  // 🚀 Lanzar servidores Python
  launchPythonServers();
});

// Manejar cierre graceful
process.on('SIGINT', () => {
  console.log('\n🛑 Cerrando servidores...');
  killPythonServers();
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.log('\n🛑 Cerrando servidores...');
  killPythonServers();
  process.exit(0);
});
