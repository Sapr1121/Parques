import express from 'express';
import cors from 'cors';
import 'dotenv/config';
import roomRoutes from './src/routes/roomRoutes';

const app = express();
app.use(cors());
app.use(express.json());

app.use('/api', roomRoutes);

const PORT = process.env.PORT ?? 3001;
app.listen(PORT, () => {
	console.log(`✅ API Node+TS lista en http://localhost:${PORT}`);
});
