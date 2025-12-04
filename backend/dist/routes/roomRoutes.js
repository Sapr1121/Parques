"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const roomController_1 = require("../controllers/roomController");
const router = (0, express_1.Router)();
router.get('/query-room', roomController_1.queryRoomController);
router.post('/create-room', roomController_1.createRoom);
exports.default = router;
