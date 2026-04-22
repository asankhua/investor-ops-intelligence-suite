import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import styled from 'styled-components';
import Sidebar from './components/Sidebar';
import Footer from './components/Footer';
import Dashboard from './pages/Dashboard';
import PillarA from './pages/PillarA';
import PillarB from './pages/PillarB';
import PillarC from './pages/PillarC';
import Evals from './pages/Evals';
import License from './pages/License';

const AppContainer = styled.div`
  display: flex;
  min-height: 100vh;
  background: linear-gradient(135deg, #E8F4FC 0%, #FFFFFF 100%);
`;

const ContentWrapper = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  margin-left: 60px;
  min-height: 100vh;
`;

const MainContent = styled.main`
  flex: 1;
  padding: 20px 20px 60px 20px;
  overflow-y: auto;
`;

function App() {
  return (
    <Router>
      <AppContainer>
        <Sidebar />
        <ContentWrapper>
          <MainContent>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/knowledge-base" element={<PillarA />} />
              <Route path="/weekly-pulse" element={<PillarB />} />
              <Route path="/voice-scheduler" element={<PillarC />} />
              <Route path="/hitl" element={<Navigate to="/voice-scheduler" replace />} />
              <Route path="/evals" element={<Evals />} />
              <Route path="/license" element={<License />} />
            </Routes>
          </MainContent>
          <Footer />
        </ContentWrapper>
      </AppContainer>
    </Router>
  );
}

export default App;
