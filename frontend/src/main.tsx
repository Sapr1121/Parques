import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import { SocketProvider } from './contexts/SocketContext';


ReactDOM.createRoot(document.getElementById('root')!).render(
  // StrictMode deshabilitado temporalmente para evitar doble ejecución de efectos
  // <React.StrictMode>
    <SocketProvider>       
      <App />
    </SocketProvider>
  // </React.StrictMode>
);