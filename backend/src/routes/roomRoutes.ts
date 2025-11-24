import { Router } from 'express';
import { createRoom } from '../controllers/roomController';

const router = Router();

router.post('/create-room', createRoom);

export default router;