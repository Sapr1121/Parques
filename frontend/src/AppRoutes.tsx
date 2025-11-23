import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Board from './components/Board/Board';
import MainMenu from './components/Lobby/MainMenu'; // Importa el nuevo componente


const AppRoutes = () => (
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<MainMenu />} />
      <Route path="/board" element={<Board />} />
    </Routes>
  </BrowserRouter>
);

export default AppRoutes;