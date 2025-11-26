import { Router } from 'express';
import { createRoom, queryRoomController } from '../controllers/roomController';

const router = Router();


router.get('/query-room', queryRoomController);
router.post('/create-room', createRoom);

export default router;