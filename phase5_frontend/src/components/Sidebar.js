import React from 'react';
import { NavLink } from 'react-router-dom';
import styled from 'styled-components';
import { Home, BookOpen, BarChart3, Mic, Activity } from 'lucide-react';

const SidebarContainer = styled.nav`
  position: fixed;
  left: 0;
  top: 0;
  width: 60px;
  height: 100vh;
  background: #1E3A5F;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 0;
  z-index: 1000;
`;

const NavItem = styled(NavLink)`
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  color: #5DADE2;
  text-decoration: none;
  margin-bottom: 8px;
  transition: all 0.2s ease;
  position: relative;

  &:hover {
    background: rgba(93, 173, 226, 0.2);
    color: #FFFFFF;
  }

  &.active {
    background: #5DADE2;
    color: #FFFFFF;
  }

  /* Tooltip */
  &::after {
    content: attr(data-label);
    position: absolute;
    left: 60px;
    background: #1E3A5F;
    color: white;
    padding: 6px 12px;
    border-radius: 4px;
    font-size: 12px;
    white-space: nowrap;
    opacity: 0;
    visibility: hidden;
    transition: all 0.2s ease;
    pointer-events: none;
  }

  &:hover::after {
    opacity: 1;
    visibility: visible;
  }
`;


const Sidebar = () => {
  return (
    <SidebarContainer>
      <NavItem to="/" data-label="Home (Dashboard)" end>
        <Home size={24} />
      </NavItem>
      
      <NavItem to="/knowledge-base" data-label="Smart-Sync Knowledge Base">
        <BookOpen size={24} />
      </NavItem>
      
      <NavItem to="/weekly-pulse" data-label="Insight-Driven Pulse">
        <BarChart3 size={24} />
      </NavItem>
      
      <NavItem to="/voice-scheduler" data-label="AI Voice Scheduler & Approvals">
        <Mic size={24} />
      </NavItem>
      
      <NavItem to="/evals" data-label="Evals: Testing & Monitoring">
        <Activity size={24} />
      </NavItem>
    </SidebarContainer>
  );
};

export default Sidebar;
