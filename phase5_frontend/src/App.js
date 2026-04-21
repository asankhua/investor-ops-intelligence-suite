import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import styled from 'styled-components';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import PillarA from './pages/PillarA';
import PillarB from './pages/PillarB';
import PillarC from './pages/PillarC';
import Evals from './pages/Evals';

const AppContainer = styled.div`
  display: flex;
  min-height: 100vh;
  background: linear-gradient(135deg, #E8F4FC 0%, #FFFFFF 100%);
`;

const MainContent = styled.main`
  flex: 1;
  margin-left: 60px;
  padding: 20px;
  overflow-y: auto;
`;

function App() {
  return (
    <Router>
      <AppContainer>
        <Sidebar />
        <MainContent>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/knowledge-base" element={<PillarA />} />
            <Route path="/weekly-pulse" element={<PillarB />} />
            <Route path="/voice-scheduler" element={<PillarC />} />
            <Route path="/hitl" element={<Navigate to="/voice-scheduler" replace />} />
            <Route path="/evals" element={<Evals />} />
          </Routes>
        </MainContent>
      </AppContainer>
    </Router>
  );
}

export default App;
