import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Board from './board/Board';
import BoardGame from './board/BoardGame';
import DeterminarTurno from './board/pages/DeterminarTurno';
import MainMenu from './Mainlobby/MainMenu';
import { NetworkTest } from "./network/components/test"; 
import { CreateRoom } from './createroom/pages/lobby';
import  JoinRoom  from './joinroom/pages/JoinRoom';
import Lobby from './joinroom/pages/Lobby';
import LoginRegister from './auth/pages/LoginRegister';
import Estadisticas from './stats/pages/Estadisticas';

const AppRoutes = () => (
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<MainMenu />} />
      <Route path="/auth" element={<LoginRegister />} />
      <Route path="/estadisticas" element={<Estadisticas />} />
      <Route path="/board" element={<Board />} />
      <Route path="/game" element={<BoardGame />} />
      <Route path="/network-test" element={<NetworkTest />} /> 
      <Route path="/create-room" element={<CreateRoom />} />
      <Route path="/join-room" element={<JoinRoom />} />
      <Route path="/lobby" element={<Lobby />} />
      <Route path="/determinar-turno" element={<DeterminarTurno />} />
    </Routes>
  </BrowserRouter>
);

export default AppRoutes;