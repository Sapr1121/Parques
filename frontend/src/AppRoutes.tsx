import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Board from './board/Board';
import MainMenu from './Mainlobby/MainMenu';
import { NetworkTest } from "./network/components/test"; 
import { CreateRoom } from './createroom/pages/lobby';
import  JoinRoom  from './joinroom/pages/JoinRoom';

const AppRoutes = () => (
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<MainMenu />} />
      <Route path="/board" element={<Board />} />
      <Route path="/network-test" element={<NetworkTest />} /> 
      <Route path="/create-room" element={<CreateRoom />} />
      <Route path="/join-room" element={<JoinRoom />} />
    </Routes>
  </BrowserRouter>
);

export default AppRoutes;