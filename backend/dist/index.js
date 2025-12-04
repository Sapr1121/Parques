"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = __importDefault(require("express"));
const cors_1 = __importDefault(require("cors"));
require("dotenv/config");
const roomRoutes_1 = __importDefault(require("./routes/roomRoutes"));
const pythonService_1 = require("./services/pythonService");
const app = (0, express_1.default)();
app.use((0, cors_1.default)());
app.use(express_1.default.json());
app.use('/api', roomRoutes_1.default);
const PORT = process.env.PORT ?? 3001;
app.listen(PORT, () => {
    console.log(`✅ API Node+TS lista en http://localhost:${PORT}`);
    // 🚀 Lanzar servidores Python
    (0, pythonService_1.launchPythonServers)();
});
// Manejar cierre graceful
process.on('SIGINT', () => {
    console.log('\n🛑 Cerrando servidores...');
    (0, pythonService_1.killPythonServers)();
    process.exit(0);
});
process.on('SIGTERM', () => {
    console.log('\n🛑 Cerrando servidores...');
    (0, pythonService_1.killPythonServers)();
    process.exit(0);
});
