# Investor Ops & Intelligence Suite - Wireframes & Frontend Guide

Complete wireframe layouts and frontend implementation guide for all three pillars.

**Design Pattern**: **Sidebar Navigation** (Single Entry Point) - All pillars accessible via left sidebar navigation within a unified dashboard.

**Technical Constraints Implemented**:
- ✅ **Single Entry Point**: One UI with sidebar for all pillars
- ✅ **No PII**: Components use `[REDACTED]` tokens for sensitive data
- ✅ **State Persistence**: Booking codes visible across pillar views
- ✅ **Light Blue Theme**: All pages use Light Blue (#E8F4FC) background - Professional, no dark theme

---

## Table of Contents

0. [Dashboard (Home + Sidebar Navigation)](#0-dashboard-home--sidebar-navigation)
1. [Frontend Technology Stack](#1-frontend-technology-stack)
2. [RAG Chat UI (Smart-Sync Knowledge Base)](#2-pillar-a-rag-chat-ui)
3. [Theme Classification & Weekly Pulse UI](#3-pillar-b-theme-classification--weekly-pulse-ui)
4. [Voice Agent & Booking UI](#4-pillar-c-voice-agent--booking-ui)
5. [HITL Approval Center](#5-hitl-approval-center)
6. [Pipeline Status UI](#6-pipeline-status-ui)
7. [Cross-Cutting Components](#7-cross-cutting-components)

---

## 0. Dashboard (Home + Sidebar Navigation)

**Technical Constraint**: Single Entry Point - All pillars accessible from one UI.

### Design Theme

**Background**: Light Blue (#E8F4FC) - Consistent across all pillars for professional look
**Primary Color**: Navy Blue (#1E3A5F) - Headers, sidebar, and key elements
**Accent Color**: Sky Blue (#5DADE2) - Interactive elements, buttons, highlights
**Text**: Dark Slate (#2C3E50) - High contrast on light background
**Cards**: White (#FFFFFF) with subtle shadow - Content containers

### Quick Use Tips

> 💡 **Tip**: Click 🏠 **Home** in sidebar to see the dashboard overview with all pillars summary and quick stats.
>
> 💡 **Tip**: Use the compact icon sidebar (📊, 📈, 🎙️, ⚙️, 📊) to quickly navigate between modules.
>
> 💡 **Tip**: 🏠 Home shows real-time stats: KB docs count, active themes, recent bookings.
>
> 💡 **Tip**: Hover over sidebar icons to see full labels: Smart-Sync KB, Insight-Driven Pulse, AI Voice Scheduler, HITL (Approval), Evals (Testing).

### Home View (Dashboard Overview)

When user clicks 🏠 **Home** in sidebar, the main content area displays an interactive, professional dashboard:

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                    INTERACTIVE HOME DASHBOARD [BG: Gradient #E8F4FC → #FFFFFF]                     │
├─────────────────────────────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌───────────────────────────────────────────────────────────────────────────────┐ │
│  │  🏠 H    │  │  🔍 Investor Intelligence Suite                              � [User ▼]     │ │
│  │  � A    │  │                                                                              │ │
│  │  📈 B    │  ├───────────────────────────────────────────────────────────────────────────────┤ │
│  │  🎙️ C    │  │                                                                              │ │
│  │  ⚙️ H    │  │    ┌────────────────────────────────────────────────────────────────────┐  │ │
│  │  📊 E    │  │    │  👋 Good Morning, User!     [🌅]    │  📅 Mon, Jan 20, 2025              │  │ │
│  │  [2] ⚡  │  │    │                                                                              │  │ │
│  └──────────┘  │    │    🏆 Dashboard Performance Score: 94/100  [▓▓▓▓▓▓▓▓▓░] 🎯              │  │ │
│               │    │    All systems operational • 12 new insights today                         │  │ │
│  [Hover for  │    └────────────────────────────────────────────────────────────────────┘  │ │
│   labels]     │                                                                              │ │
│               │    🚀 PILLARS OVERVIEW                                                        │ │
│               │    ┌────────────────────────────────────────────────────────────────────────┐ │ │
│               │    │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐    │ │ │
│               │    │  │ 📚 PILLAR A       │  │ 📈 PILLAR B       │  │ 🎙️ PILLAR C       │    │ │ │
│               │    │  │                   │  │                   │  │                   │    │ │ │
│               │    │  │  Self-RAG KB      │  │  Theme Analysis   │  │  AI Voice Agent   │    │ │ │
│               │    │  │  ┌───────────────┐│  │  ┌───────────────┐│  │  ┌───────────────┐│    │ │ │
│               │    │  │  │ 5,000+ Docs   ││  │  │ 3 Themes 🟢🟡🔴││  │  │ 12 Bookings   ││    │ │ │
│               │    │  │  │ 📈 +15% ↑     ││  │  │ Top: Login    ││  │  │ This Week     ││    │ │ │
│               │    │  │  └───────────────┘│  │  └───────────────┘│  │  └───────────────┘│    │ │ │
│               │    │  │  [🚀 Launch →]    │  │  [📊 Analyze →]   │  │  [🎙️ Book Now →]  │    │ │ │
│               │    │  └─────────────────┘  └─────────────────┘  └─────────────────┘    │ │ │
│               │    │                                                                              │ │ │
│               │    │  ┌─────────────────────────────────────┐  ┌─────────────────────────┐  │ │ │
│               │    │  │ ⚙️ HITL Center                      │  │ 📊 Testing Suite        │  │ │ │
│               │    │  │  2 Pending Approvals 🔴           │  │  ✅ All Tests Passed    │  │ │ │
│               │    │  │  [📅 Calendar] [📧 Email]          │  │  3 Pipelines Active     │  │ │ │
│               │    │  │  [View All →]                       │  │  [View Metrics →]       │  │ │ │
│               │    │  └─────────────────────────────────────┘  └─────────────────────────┘  │ │ │
│               │    └────────────────────────────────────────────────────────────────────────┘ │ │
│               │                                                                              │ │
│               │    📊 LIVE ACTIVITY FEED                                                      │ │
│               │    ┌────────────────────────────────────────────────────────────────────┐    │ │
│               │    │ 🔥 Recent Activity (Last 24 Hours)                                  │    │ │
│               │    │ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │    │ │
│               │    │ [12:30] ✅ Theme analysis generated • 3 themes detected          │    │ │
│               │    │ [11:45] 🎙️ New booking: MTG-2024-007 confirmed                     │    │ │
│               │    │ [10:20] 📚 Knowledge base updated • 15 new documents indexed         │    │ │
│               │    │ [09:15] ⚙️ HITL: Calendar hold approved for advisor meeting        │    │ │
│               │    │                                                                      │    │ │
│               │    │ [ View Full Activity Report →]                                   │    │ │
│               │    └────────────────────────────────────────────────────────────────────┘    │ │
│               │                                                                              │ │
│               │    ⚡ QUICK ACTIONS                                                          │ │
│               │    ┌────────────────────────────────────────────────────────────────────┐    │ │
│               │    │ [� Quick Search KB]  [📈 Generate Weekly Pulse]  [🎙️ Voice Booking]  │    │ │
│               │    │ [⚙️ Review Pending (2)]  [� View Analytics]  [🔄 Refresh All Data]      │    │ │
│               │    └────────────────────────────────────────────────────────────────────┘    │ │
│               │                                                                              │ │
└─────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Implementation Notes

**React + Ant Design Example**:

```jsx
import { Layout, Menu, Button, Card, Space, Badge } from 'antd';
import { 
  HomeOutlined, DatabaseOutlined, BarChartOutlined, 
  AudioOutlined, SettingOutlined, ExperimentOutlined,
  ArrowRightOutlined, SearchOutlined, BellOutlined
} from '@ant-design/icons';

const { Sider, Content, Header } = Layout;

const Dashboard = () => {
  const menuItems = [
    { key: 'home', icon: <HomeOutlined />, label: '🏠 H', title: 'Home' },
    { key: 'pillar-a', icon: <DatabaseOutlined />, label: '📊', title: 'Smart-Sync Knowledge Base' },
    { key: 'pillar-b', icon: <BarChartOutlined />, label: '📈', title: 'Insight-Driven Pulse' },
    { key: 'pillar-c', icon: <AudioOutlined />, label: '🎙️', title: 'AI Voice Scheduler' },
    { key: 'hitl', icon: <SettingOutlined />, label: '⚙️ H', title: 'HITL Center', badge: 2 },
    { key: 'evals', icon: <ExperimentOutlined />, label: '📊 E', title: 'Evals: Test Suite' }
  ];

  return (
    <Layout style={{ minHeight: '100vh', background: '#E8F4FC' }}>
      {/* Compact Icon Sidebar */}
      <Sider 
        width={60} 
        style={{ background: '#1E3A5F', padding: '16px 0' }}
      >
        <Menu
          mode="vertical"
          style={{ background: '#1E3A5F', border: 'none' }}
          items={menuItems.map(item => ({
            key: item.key,
            icon: (
              <div style={{ color: '#FFFFFF', fontSize: '18px' }}>
                {item.icon} {item.badge && <Badge count={item.badge} size="small" />}
              </div>
            ),
            label: <span style={{ color: '#FFFFFF', fontSize: '12px' }}>{item.label}</span>,
            title: item.title
          }))}
        />
      </Sider>
      
      <Layout>
        {/* Header */}
        <Header style={{ background: '#FFFFFF', padding: '0 24px', display: 'flex', justifyContent: 'space-between' }}>
          <span style={{ fontWeight: 'bold', color: '#1E3A5F' }}>🔍 Investor Intelligence Suite</span>
          <Space>
            <Button icon={<SearchOutlined />} />
            <Button icon={<BellOutlined />} />
            <span>👤 User</span>
          </Space>
        </Header>
        
        {/* Main Content */}
        <Content style={{ padding: '24px', background: '#E8F4FC' }}>
          {/* Content changes based on sidebar selection */}
        </Content>
      </Layout>
    </Layout>
  );
};
```

### Key Interactive Elements

1. **Animated Hero Icons**: Three pillar icons float/bounce subtly to draw attention
2. **Interactive Demo**: Working RAG chatbot preview (limited to 3 queries without auth)
3. **Hover Effects**: Cards lift on hover with shadow increase
4. **Smooth Scroll**: Navigation links scroll to sections
5. **CTA Buttons**: Primary (Navy) and Secondary (Outlined) styles

### Implementation

```jsx
// LandingPage.jsx
import React, { useState } from 'react';
import { Button, Card, Input, Badge } from 'antd';
import { MessageOutlined, BarChartOutlined, AudioOutlined, ArrowRightOutlined } from '@ant-design/icons';

const LandingPage = () => {
  const [demoQuery, setDemoQuery] = useState('');
  const [demoResponse, setDemoResponse] = useState(null);

  const handleDemoSubmit = async () => {
    // Call RAG API with limited free tier
    const response = await fetch('/api/demo/rag', {
      method: 'POST',
      body: JSON.stringify({ query: demoQuery })
    });
    setDemoResponse(await response.json());
  };

  return (
    <div className="landing-page" style={{ background: 'linear-gradient(180deg, #E8F4FC 0%, #FFFFFF 100%)' }}>
      {/* Navigation */}
      <nav className="landing-nav" style={{ background: '#FFFFFF', padding: '16px 48px' }}>
        <div className="logo" style={{ color: '#1E3A5F', fontWeight: 'bold' }}>
          🏢 Investor Suite
        </div>
        <div className="nav-links">
          <Button type="text">Features</Button>
          <Button type="text">Solutions</Button>
          <Button type="primary" style={{ background: '#1E3A5F' }}>Sign In</Button>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="hero" style={{ textAlign: 'center', padding: '80px 48px' }}>
        <h1 style={{ color: '#1E3A5F', fontSize: '48px', marginBottom: '24px' }}>
          🤖 Investor Intelligence Suite
        </h1>
        <p style={{ color: '#2C3E50', fontSize: '24px', marginBottom: '48px' }}>
          One Platform. Three Pillars. Infinite Insights.
        </p>
        
        {/* Floating Pillar Icons - Click any to navigate to Unified Dashboard */}
        <div className="pillar-icons" style={{ display: 'flex', justifyContent: 'center', gap: '32px', marginBottom: '48px' }}>
          <Card className="pillar-card" style={{ width: 120, textAlign: 'center', background: '#FFFFFF' }}>
            <MessageOutlined style={{ fontSize: 48, color: '#5DADE2' }} />
            <div>Pillar A</div>
          </Card>
          <Card className="pillar-card" style={{ width: 120, textAlign: 'center', background: '#FFFFFF' }}>
            <BarChartOutlined style={{ fontSize: 48, color: '#5DADE2' }} />
            <div>Pillar B</div>
          </Card>
          <Card className="pillar-card" style={{ width: 120, textAlign: 'center', background: '#FFFFFF' }}>
            <AudioOutlined style={{ fontSize: 48, color: '#5DADE2' }} />
            <div>Pillar C</div>
          </Card>
        </div>

        <Button type="primary" size="large" style={{ background: '#1E3A5F', marginRight: 16 }}>
          🚀 Launch Unified Dashboard <ArrowRightOutlined />
        </Button>
        <Button size="large">▶️ Watch Demo</Button>
      </section>

      {/* Interactive Demo */}
      <section className="demo-section" style={{ padding: '48px', background: '#E8F4FC' }}>
        <h2 style={{ color: '#1E3A5F', textAlign: 'center' }}>⚡ Try It Now - No Login Required</h2>
        <Card style={{ maxWidth: 800, margin: '0 auto', background: '#FFFFFF' }}>
          <div className="chat-demo">
            <div className="message bot" style={{ background: '#E8F4FC', padding: 12, borderRadius: 8, marginBottom: 12 }}>
              🤖 Hello! Ask me about any fund. Try: "What is the exit load for HDFC Top 100?"
            </div>
            <Input.Search
              placeholder="Type your question..."
              value={demoQuery}
              onChange={(e) => setDemoQuery(e.target.value)}
              onSearch={handleDemoSubmit}
              enterButton="Ask"
            />
            {demoResponse && (
              <div className="response" style={{ marginTop: 16, padding: 12, background: '#F6F8FA', borderRadius: 8 }}>
                {demoResponse.answer}
              </div>
            )}
          </div>
          <div style={{ textAlign: 'center', marginTop: 12, color: '#5DADE2' }}>
            <Badge count="3" style={{ backgroundColor: '#5DADE2' }} /> free queries remaining
          </div>
        </Card>
      </section>

      {/* Footer */}
      <footer style={{ background: '#1E3A5F', color: '#FFFFFF', padding: '24px 48px', textAlign: 'center' }}>
        © 2026 Investor Intelligence Suite | <a href="#" style={{ color: '#5DADE2' }}>Privacy</a> | <a href="#" style={{ color: '#5DADE2' }}>Terms</a>
      </footer>
    </div>
  );
};
```

---

## 0. Dashboard (Home + Sidebar Navigation)

**Technical Constraint**: Single Entry Point - All pillars accessible from one UI.

### Design Theme

**Background**: Light Blue (#E8F4FC) - Consistent across all pillars for professional look
**Primary Color**: Navy Blue (#1E3A5F) - Headers, sidebar, and key elements
**Accent Color**: Sky Blue (#5DADE2) - Interactive elements, buttons, highlights
**Text**: Dark Slate (#2C3E50) - High contrast on light background
**Cards**: White (#FFFFFF) with subtle shadow - Content containers
**Sidebar**: Navy Blue (#1E3A5F) with white text - Navigation contrast

### Quick Use Tips

> 💡 **Tip**: Use the compact icon sidebar (📊A, 📈B, 🎙️C, ⚙️H, 📊E) to switch between all pillars. Hover over icons to see full labels.
> 
> 💡 **Tip**: The HITL badge shows pending approvals requiring your attention.
> 
> 💡 **Tip**: All pillars share the same state - booking codes from Voice Agent appear in Weekly Pulse notes automatically.

### Implementation Note

> **Framework**: Implement using your preferred frontend framework (React, Vue, Vanilla JS, etc.).
> The wireframes above specify the **UI structure** - implementation details are framework-agnostic.

### Implementation with Sidebar

```jsx
// UnifiedDashboard.jsx
import React, { useState } from 'react';
import { Layout, Menu, Badge } from 'antd';  // or custom components
import RAGChat from './RAGChat';
import WeeklyPulse from './WeeklyPulse';
import VoiceAgent from './VoiceAgent';
import HITLCenter from './HITLCenter';
import EvalSuite from './EvalSuite';

const { Sider, Content, Header, Footer } = Layout;

const UnifiedDashboard = () => {
  const [selectedPillar, setSelectedPillar] = useState('pillar-a');
  const [pendingCount, setPendingCount] = useState(2);

  const menuItems = [
    { key: 'pillar-a', icon: '�', label: 'A', title: 'Pillar A: Self-RAG KB' },
    { key: 'pillar-b', icon: '📈', label: 'B', title: 'Pillar B: Weekly Pulse' },
    { key: 'pillar-c', icon: '🎙️', label: 'C', title: 'Pillar C: Voice + Book' },
    { 
      key: 'hitl', 
      icon: '⚙️', 
      label: 'H',
      title: 'HITL Center',
      badge: pendingCount > 0 ? pendingCount : null
    },
    { key: 'evals', icon: '📊', label: 'E', title: 'Evals: Test Suite' }
  ];

  const renderContent = () => {
    switch(selectedPillar) {
      case 'pillar-a': return <RAGChat />;
      case 'pillar-b': return <WeeklyPulse />;
      case 'pillar-c': return <VoiceAgent />;
      case 'hitl': return <HITLCenter />;
      case 'evals': return <EvalSuite />;
      default: return <RAGChat />;
    }
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      {/* Sidebar Navigation */}
      <Sider width={280} theme="light" style={{ borderRight: '1px solid #e8e8e8' }}>
        <div style={{ padding: '16px', fontWeight: 'bold', fontSize: '18px' }}>
          📊 Investor Suite
        </div>
        
        <Menu
          mode="inline"
          selectedKeys={[selectedPillar]}
          items={menuItems}
          onClick={({ key }) => setSelectedPillar(key)}
        />
        
        {/* Technical Constraints Footer in Sidebar */}
        <div style={{ 
          position: 'absolute', 
          bottom: 0, 
          width: '100%', 
          padding: '16px',
          borderTop: '1px solid #e8e8e8',
          background: '#f5f5f5'
        }}>
          <div style={{ fontSize: '12px', color: '#666', marginBottom: '8px' }}>
            Technical Constraints
          </div>
          <div style={{ fontSize: '11px', color: '#52c41a' }}>✓ Single Entry Point</div>
          <div style={{ fontSize: '11px', color: '#52c41a' }}>✓ No PII Leaks</div>
          <div style={{ fontSize: '11px', color: '#52c41a' }}>✓ State Persistence</div>
        </div>
      </Sider>

      {/* Main Content */}
      <Layout>
        <Header style={{ background: '#fff', padding: '0 24px', borderBottom: '1px solid #e8e8e8' }}>
          <h2 style={{ margin: 0 }}>Investor Ops & Intelligence Suite</h2>
        </Header>
        
        <Content style={{ margin: '24px', padding: '24px', background: '#fff', minHeight: 280 }}>
          {renderContent()}
        </Content>
        
        <Footer style={{ textAlign: 'center', background: '#f0f2f5' }}>
          Unified Dashboard | All 3 Pillars | Single Entry Point ✓
        </Footer>
      </Layout>
    </Layout>
  );
};

export default UnifiedDashboard;
```

### CSS for Sidebar Layout

```css
/* unified-dashboard.css */

.unified-dashboard {
  display: flex;
  min-height: 100vh;
}

/* Sidebar Styles */
.sidebar {
  width: 280px;
  background: #f8f9fa;
  border-right: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
  position: fixed;
  height: 100vh;
  overflow-y: auto;
}

.sidebar-header {
  padding: 20px;
  font-size: 18px;
  font-weight: bold;
  color: #333;
  border-bottom: 1px solid #e0e0e0;
}

.sidebar-nav {
  flex: 1;
  padding: 16px 0;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  cursor: pointer;
  transition: background 0.2s;
  border-left: 3px solid transparent;
}

.nav-item:hover {
  background: #e8e8e8;
}

.nav-item.active {
  background: #e3f2fd;
  border-left-color: #2196f3;
}

.nav-icon {
  font-size: 20px;
  margin-right: 12px;
  width: 24px;
  text-align: center;
}

.nav-label {
  font-size: 14px;
  color: #555;
}

.nav-badge {
  margin-left: auto;
  background: #f44336;
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
}

/* Sidebar Footer - Constraints */
.sidebar-footer {
  padding: 16px 20px;
  background: #f0f0f0;
  border-top: 1px solid #e0e0e0;
}

.constraint-title {
  font-size: 11px;
  color: #666;
  text-transform: uppercase;
  margin-bottom: 8px;
  letter-spacing: 0.5px;
}

.constraint-item {
  font-size: 12px;
  color: #4caf50;
  margin: 4px 0;
}

/* Main Content */
.main-content {
  flex: 1;
  margin-left: 280px;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.main-header {
  background: white;
  padding: 16px 24px;
  border-bottom: 1px solid #e0e0e0;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.main-header h1 {
  margin: 0;
  font-size: 20px;
  color: #333;
}

.content-area {
  flex: 1;
  padding: 24px;
  background: #f5f5f5;
  overflow-y: auto;
}

.pillar-container {
  background: white;
  border-radius: 8px;
  padding: 24px;
  min-height: 600px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

/* Footer */
.dashboard-footer {
  background: white;
  padding: 16px 24px;
  border-top: 1px solid #e0e0e0;
  text-align: center;
  color: #666;
  font-size: 14px;
}

.constraints-bar {
  display: flex;
  justify-content: center;
  gap: 32px;
  margin-top: 8px;
}

.constraint-status {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #4caf50;
}
```

---

## 1. Frontend Technology Stack

### Technology Options

| Feature | React | Vanilla JS | HTML/CSS |
|---------|-------|------------|----------|
| **Setup Time** | 30 min | 20 min | 15 min |
| **Audio Recording** | MediaRecorder API | MediaRecorder API | MediaRecorder API |
| **Pipeline Status UI** | Components + hooks | DOM manipulation | DOM manipulation |
| **Chat Interface** | Custom components | Dynamic DOM | Static + minimal JS |
| **State Management** | useState / Redux | LocalStorage | localStorage |
| **Styling** | CSS-in-JS / Tailwind | CSS / SASS | CSS |
| **Backend Coupling** | Loose (any API) | Loose (any API) | Loose (any API) |
| **Production Ready** | Yes | Yes | Yes |

### Architecture Patterns

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    FRONTEND ARCHITECTURE                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  REACT / VANILLA JS / HTML-CSS (Production-Ready)                       │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────┐            │
│  │   React /    │      │  FastAPI     │      │  Python  │            │
│  │  Vanilla JS  │◄────►│  Backend     │◄────►│  Agents  │            │
│  │   HTML/CSS   │ REST │  (Python)    │      │          │            │
│  │              │      │              │      │          │            │
│  │ • Components │      │ • API routes │      │ • RAG    │            │
│  │ • Hooks      │      │ • WebSocket  │      │ • MCP    │            │
│  │ • CSS/Styled │      │ • Auth       │      │ • Voice  │            │
│  │ • Media API  │      │ • State      │      │ • Logic  │            │
│  └──────────────┘      └──────────────┘      └──────────┘            │
│                                                                         │
│  Benefits: Full control, scalable, framework-agnostic backend, any API   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Dependencies

**Backend (Python)**
```txt
# API Framework
fastapi>=0.104.0
uvicorn>=0.24.0
python-multipart>=0.0.6  # For audio file uploads

# Core
langchain>=0.3.0
langgraph>=0.2.0
```

**Frontend**

**Option A: React**
```bash
# Create React app
npx create-react-app investor-suite-ui

# Or with Vite (faster)
npm create vite@latest investor-suite-ui -- --template react

# Required packages
npm install axios  # For API calls
```

**Option B: Vanilla JS**
```html
<!-- No build step required -->
<!-- Just HTML + CSS + JS files -->
```

---

## 2. RAG Chat UI (Smart-Sync Knowledge Base)

> **Note**: This is the **content component** that renders in the main area when "📚 Smart-Sync Knowledge Base" is selected from the sidebar (Section 0).

### Quick Use Tips

> 💡 **Tip**: Select a fund from the left panel to start a conversation. All responses follow the 6-bullet structure with source citations.
> 
> 💡 **Tip**: Click on any citation link [M1, M2, M1.1] in the right panel to view the source document.

### Design Theme

**Background**: Light Blue (#E8F4FC) - Professional, clean, easy on the eyes
**Primary Color**: Navy Blue (#1E3A5F) - Headers and key elements
**Accent Color**: Sky Blue (#5DADE2) - Interactive elements and highlights
**Text**: Dark Slate (#2C3E50) - High contrast for readability
**Cards**: White (#FFFFFF) with subtle shadow - Clean content containers

### Wireframe Layout

```
┌───────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│  📊 PILLAR A: SMART-SYNC KNOWLEDGE BASE                     [Light Blue Background #E8F4FC]                │
├───────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                           │
│  ┌─────────────────────┐   ┌──────────────────────────────────────────────────────────┐   ┌─────────────┐ │
│  │ 📋 FUND LIST        │   │ 💬 CONVERSATIONAL CHAT AREA                              │   │ 📄 SOURCES  │ │
│  │ [White Card #FFF]   │   │ [White Card #FFF]                                        │   │ [White Card]│ │
│  │                     │   │                                                          │   │             │ │
│  │ 🔍 Search Funds...  │   │ ┌─────────────────────────────────────────────────────┐  │   │ 6-BULLET    │ │
│  │ ┌─────────────────┐ │   │ │ 🤖 AI Advisor                                        │  │   │ STRUCTURE   │ │
│  │ │ Type to search  │ │   │ │ ─────────────────────────────────────────────────    │  │   │             │ │
│  │ └─────────────────┘ │   │ │                                                      │  │   │ • Exit load │ │
│  │                     │   │ │ 👤 You: What is the exit load for ELSS fund?         │  │   │   for ELSS  │ │
│  │ ▼ HDFC Top 100     │   │ │                                                      │  │   │   is 1%...  │ │
│  │   SBI Blue Chip    │   │ │ 🤖 Advisor: Based on your query, here are the facts: │  │   │             │ │
│  │   Axis Midcap      │   │ │                                                      │  │   │ • ELSS has  │ │
│  │   ICICI Pru Value  │   │ │ • Exit load for ELSS is 1% if redeemed within      │  │   │   3-year... │ │
│  │   Nippon India     │   │ │   1 year [Source: M1.1]                              │  │   │             │ │
│  │   Canara Robeco    │   │ │ • ELSS funds have a 3-year lock-in period          │  │   │ • Exit load │ │
│  │   Kotak Equity     │   │ │   [Source: M1]                                     │  │   │   applies...│ │
│  │   DSP Mid Cap      │   │ │ • Exit load applies only to units purchased          │  │   │             │ │
│  │   HDFC Small Cap   │   │ │   within 1 year [Source: M1.1]                     │  │   │ [M1.1]      │ │
│  │   L&T Midcap       │   │ │                                                      │  │   │ [M1]        │ │
│  │   Motilal Oswal    │   │ │ • Early redemption attracts 1% charge              │  │   │ [View Doc]  │ │
│  │   PGIM India       │   │ │ • Tax benefits available after 3-year lock-in       │  │   │             │ │
│  │   Tata Digital     │   │ │ • Exit load calculated on redemption value           │  │   │ ───────────│ │
│  │   UTI Nifty 50     │   │ │                                                      │  │   │ 🔗 Sources  │ │
│  │                     │   │ └─────────────────────────────────────────────────────┘  │   │             │ │
│  │ [Scrollable List]  │   │                                                          │   │             │ │
│  │                     │   │ ┌─────────────────────────────────────────────────────┐  │   │             │ │
│  │                     │   │ │ 💬 Type your question...                    [🔍]  │  │   │             │ │
│  │                     │   │ └─────────────────────────────────────────────────────┘  │   │             │ │
│  └─────────────────────┘   └──────────────────────────────────────────────────────────┘   │ [View Source]│ │
│                                                                                           │ [View Source]│ │
│  📊 Self-RAG Debug Panel (Collapsible - Light Blue Tint #D6EAF8)                           │              │ │
│  ┌──────────────────────────────────────────────────────────────────────────────────────┐ │              │ │
│  │ 🔍 Query Expansion    │ 🧠 Sufficiency Check    │ 📄 Retrieved Chunks              │ │              │ │
│  │ Original: "Why..."    │ Status: ✅ Sufficient   │ ┌────────┬────────┬───────────┐ │ │              │ │
│  │ Variants: 3           │ Reason: "Chunks..."     │ │Chunk # │ Source │ Preview   │ │ │              │ │
│  └──────────────────────────────────────────────────────────────────────────────────────┘ └──────────────┘ │
│                                                                                                           │
└───────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Implementation

**Option A: React**
```jsx
// RAGChat.jsx
import React, { useState } from 'react';
import axios from 'axios';

const RAGChat = () => {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showDebug, setShowDebug] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const result = await axios.post('/api/v1/query', { query });
      setResponse(result.data);
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="rag-chat">
      <h1>📊 Smart-Sync Knowledge Base</h1>
      
      <form onSubmit={handleSearch} className="search-form">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask about mutual funds..."
          className="search-input"
        />
        <button type="submit" disabled={loading} className="search-btn">
          {loading ? 'Searching...' : '🔍 Search'}
        </button>
      </form>
      
      {response && (
        <>
          <div className="response-card">
            <h3>📄 Response</h3>
            <ul className="bullets-list">
              {response.bullets.map((bullet, i) => (
                <li key={i} className="bullet-item">
                  <span className="bullet-num">{i + 1}.</span>
                  {bullet}
                  <span className="citation">
                    [{response.citations.find(c => c.bullet_index === i)?.source}]
                  </span>
                </li>
              ))}
            </ul>
            
            <div className="sources">
              {response.sources_used.map(source => (
                <button key={source} className="source-btn">
                  📄 See {source} Source
                </button>
              ))}
            </div>

            {/* Self-RAG Metadata */}
            <div className="rag-metadata">
              <span className="meta-tag">🔁 Loops: {response.self_rag_loops}</span>
              <span className="meta-tag">💰 Cost: ${response.cost?.toFixed(4) || 'N/A'}</span>
              <span className="meta-tag">🤖 GPT-4o via OpenRouter</span>
            </div>
          </div>

          {/* Debug Panel Toggle */}
          <button onClick={() => setShowDebug(!showDebug)} className="debug-toggle">
            {showDebug ? '🔼 Hide Debug' : '🔽 Show Debug'}
          </button>

          {/* Self-RAG Debug Panel */}
          {showDebug && (
            <div className="debug-panel">
              <h4>🔍 Self-RAG Pipeline Debug</h4>
              
              <div className="debug-section">
                <h5>Query Expansion</h5>
                <p><strong>Original:</strong> {query}</p>
                <p><strong>Variants:</strong></p>
                <ul>
                  {response.query_variants?.map((v, i) => (
                    <li key={i}>{i + 1}. {v}</li>
                  ))}
                </ul>
              </div>

              <div className="debug-section">
                <h5>🧠 Sufficiency Check</h5>
                <p>Status: {response.sufficiency?.sufficient ? '✅ Sufficient' : '❌ Re-retrieved'}</p>
                <p>Reason: {response.sufficiency?.reason}</p>
              </div>

              <div className="debug-section">
                <h5>📄 Retrieved Chunks</h5>
                <table className="chunks-table">
                  <thead>
                    <tr><th>#</th><th>Source</th><th>Preview</th></tr>
                  </thead>
                  <tbody>
                    {response.retrieved_chunks?.map((chunk, i) => (
                      <tr key={i}>
                        <td>{i + 1}</td>
                        <td>{chunk.metadata?.source}</td>
                        <td>{chunk.page_content?.substring(0, 50)}...</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="debug-footer">
                <span>Embedding: OpenRouter openai/text-embedding-3-large (3072-dim)</span>
                <span>Vector DB: Pinecone</span>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default RAGChat;
```

**Option C: Vanilla JS**
```javascript
// ragChat.js
class RAGChat {
  constructor(containerId, apiUrl = '/api/v1/query') {
    this.container = document.getElementById(containerId);
    this.apiUrl = apiUrl;
    this.lastQuery = '';
    this.showDebug = false;
    this.init();
  }

  init() {
    this.container.innerHTML = `
      <div class="rag-chat">
        <h1>📊 Smart-Sync Knowledge Base</h1>
        <form class="search-form">
          <input type="text" class="search-input" 
                 placeholder="Ask about mutual funds..." required>
          <button type="submit" class="search-btn">🔍 Search</button>
        </form>
        <div class="response-area"></div>
        <div class="debug-area"></div>
      </div>
    `;

    this.container.querySelector('.search-form').addEventListener('submit', (e) => {
      e.preventDefault();
      this.handleSearch();
    });
  }

  async handleSearch() {
    const input = this.container.querySelector('.search-input');
    const responseArea = this.container.querySelector('.response-area');
    const debugArea = this.container.querySelector('.debug-area');
    
    this.lastQuery = input.value;
    responseArea.innerHTML = '<p class="loading">Searching with Self-RAG...</p>';
    debugArea.innerHTML = '';
    
    try {
      const response = await fetch(this.apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: input.value })
      });
      
      const data = await response.json();
      this.renderResponse(data);
      this.renderDebug(data);
    } catch (error) {
      responseArea.innerHTML = `<p class="error">Error: ${error.message}</p>`;
    }
  }

  renderResponse(data) {
    const bullets = data.bullets.map((bullet, i) => {
      const citation = data.citations.find(c => c.bullet_index === i);
      return `
        <li class="bullet-item">
          <span class="bullet-num">${i + 1}.</span>
          ${bullet}
          <span class="citation">[${citation?.source || ''}]</span>
        </li>
      `;
    }).join('');

    this.container.querySelector('.response-area').innerHTML = `
      <div class="response-card">
        <h3>📄 Response</h3>
        <ul class="bullets-list">${bullets}</ul>
        <div class="sources">
          ${data.sources_used.map(s => 
            `<button class="source-btn">📄 See ${s} Source</button>`
          ).join('')}
        </div>
        <div class="rag-metadata">
          <span class="meta-tag">🔁 Loops: ${data.self_rag_loops || 0}</span>
          <span class="meta-tag">💰 Cost: $${(data.cost || 0).toFixed(4)}</span>
          <span class="meta-tag">🤖 GPT-4o via OpenRouter</span>
        </div>
        <button class="debug-toggle" onclick="this.closest('.rag-chat').dispatchEvent(new CustomEvent('toggleDebug'))">
          🔽 Show Debug
        </button>
      </div>
    `;
    
    // Add debug toggle event listener
    this.container.addEventListener('toggleDebug', () => {
      this.showDebug = !this.showDebug;
      const debugArea = this.container.querySelector('.debug-area');
      debugArea.style.display = this.showDebug ? 'block' : 'none';
      this.container.querySelector('.debug-toggle').textContent = 
        this.showDebug ? '🔼 Hide Debug' : '🔽 Show Debug';
    });
  }

  renderDebug(data) {
    const variants = data.query_variants?.map((v, i) => 
      `<li>${i + 1}. ${v}</li>`
    ).join('') || '';
    
    const chunks = data.retrieved_chunks?.map((chunk, i) => `
      <tr>
        <td>${i + 1}</td>
        <td>${chunk.metadata?.source || 'N/A'}</td>
        <td>${(chunk.page_content || '').substring(0, 50)}...</td>
      </tr>
    `).join('') || '';

    this.container.querySelector('.debug-area').innerHTML = `
      <div class="debug-panel" style="display: none;">
        <h4>🔍 Self-RAG Pipeline Debug</h4>
        
        <div class="debug-section">
          <h5>Query Expansion</h5>
          <p><strong>Original:</strong> ${this.lastQuery}</p>
          <p><strong>Variants:</strong></p>
          <ul>${variants}</ul>
        </div>

        <div class="debug-section">
          <h5>🧠 Sufficiency Check</h5>
          <p>Status: ${data.sufficiency?.sufficient ? '✅ Sufficient' : '❌ Re-retrieved'}</p>
          <p>Reason: ${data.sufficiency?.reason || 'N/A'}</p>
        </div>

        <div class="debug-section">
          <h5>📄 Retrieved Chunks</h5>
          <table class="chunks-table">
            <thead><tr><th>#</th><th>Source</th><th>Preview</th></tr></thead>
            <tbody>${chunks}</tbody>
          </table>
        </div>

        <div class="debug-footer">
          <span>Embedding: OpenRouter openai/text-embedding-3-large (3072-dim)</span>
          <span>Vector DB: Pinecone</span>
        </div>
      </div>
    `;
  }
}
```

### CSS Styles
```css
/* rag-chat.css */

.rag-chat {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.search-form {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.search-input {
  flex: 1;
  padding: 12px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
}

.search-input:focus {
  outline: none;
  border-color: #667eea;
}

.search-btn {
  padding: 12px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
}

.search-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.response-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.bullets-list {
  list-style: none;
  padding: 0;
}

.bullet-item {
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
  line-height: 1.6;
}

.bullet-num {
  font-weight: bold;
  color: #667eea;
  margin-right: 8px;
}

.citation {
  color: #666;
  font-size: 0.9rem;
  margin-left: 8px;
}

.source-btn {
  margin: 8px 8px 0 0;
  padding: 8px 16px;
  background: #f5f5f5;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  cursor: pointer;
}

.source-btn:hover {
  background: #e8e8e8;
}

/* Self-RAG Metadata Tags */
.rag-metadata {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e0e0e0;
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.meta-tag {
  background: #f0f4ff;
  color: #667eea;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
}

/* Debug Toggle Button */
.debug-toggle {
  margin-top: 16px;
  padding: 8px 16px;
  background: #f5f5f5;
  border: 1px dashed #999;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  color: #666;
}

.debug-toggle:hover {
  background: #e8e8e8;
}

/* Self-RAG Debug Panel */
.debug-panel {
  background: #f8f9fa;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
  margin-top: 16px;
}

.debug-panel h4 {
  margin: 0 0 16px 0;
  color: #333;
  font-size: 1rem;
}

.debug-section {
  margin-bottom: 16px;
  padding: 12px;
  background: white;
  border-radius: 6px;
  border-left: 3px solid #667eea;
}

.debug-section h5 {
  margin: 0 0 8px 0;
  color: #667eea;
  font-size: 0.9rem;
}

.debug-section p {
  margin: 4px 0;
  font-size: 0.9rem;
  color: #555;
}

.debug-section ul {
  margin: 8px 0;
  padding-left: 20px;
}

.debug-section li {
  font-size: 0.9rem;
  color: #666;
  margin: 4px 0;
}

.chunks-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
}

.chunks-table th,
.chunks-table td {
  padding: 8px;
  text-align: left;
  border-bottom: 1px solid #e0e0e0;
}

.chunks-table th {
  background: #f5f5f5;
  font-weight: 600;
  color: #555;
}

.chunks-table td {
  color: #666;
}

.debug-footer {
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid #e0e0e0;
  display: flex;
  gap: 16px;
  font-size: 0.8rem;
  color: #999;
}

/* Loading State */
.loading {
  text-align: center;
  color: #667eea;
  padding: 40px;
  font-style: italic;
}
```

---

## 3. Theme Classification & Weekly Pulse UI

> **Note**: This is the **content component** that renders in the main area when "📈 Insight-Driven Pulse" is selected from the sidebar (Section 0).

### Design Theme

**Background**: Light Blue (#E8F4FC) - Professional, clean, easy on the eyes
**Primary Color**: Navy Blue (#1E3A5F) - Headers and key elements
**Accent Color**: Sky Blue (#5DADE2) - Interactive elements and highlights
**Text**: Dark Slate (#2C3E50) - High contrast for readability
**Cards**: White (#FFFFFF) with subtle shadow - Clean content containers

### Quick Use Tips

> 💡 **Tip**: Reviews are processed from `/data/reviews/`. Click 📥 Download Reviews CSV to download the latest review file (e.g., `2025-04-20.json`).
> 
> 💡 **Tip**: 🔄 Refresh fetches/syncs the latest reviews from `/data/reviews/` and updates the "Last Synced" timestamp.
> 
> 💡 **Tip**: ⚡ Generate Insights processes the synced reviews to generate Theme Analysis Results and Weekly Product Pulse.
> 
> 💡 **Tip**: The 📊 Analytics Dashboard (right panel) visualizes theme distribution, sentiment trends, mention volume, and keyword clouds from the analysis results.
> 
> 💡 **Tip**: The Weekly Pulse integrates with the Voice Agent - top themes will be mentioned in greeting messages when confidence is above 0.7.

### Wireframe Layout

```
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│  📈 PILLAR B: INSIGHT-DRIVEN AGENT OPTIMIZATION     [BG: #E8F4FC]                        │
├───────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                           │
│  ┌─────────────────────────────────────────────────────┐  ┌───────────────────────────┐ │
│  │ 📊 Reviews Data Source                              │  │ 📊 Analytics Dashboard    │ │
│  │ ┌───────────────────────────────────────────────┐  │  │                           │ │
│  │ │ 📁 Source: reviews_db (auto-sync daily)      │💾│  │  ┌─────────────────────┐  │ │
│  │ │ 🕐 Last Synced: 2025-04-20 14:30 IST         │  │  │  │ Theme Distribution  │  │ │
│  │ └───────────────────────────────────────────────┘  │  │  │ 📊 Pie Chart        │  │ │
│  │ [📥 Download CSV] [🔄 Refresh] [⚡ Generate]        │  │  │  │ 🔴Login 🟢Ret 🟡Fee│  │ │
│  └─────────────────────────────────────────────────────┘  │  └─────────────────────┘  │ │
│                                                           │                           │ │
│  ┌─────────────────────────────────────────────────────┐  │  ┌─────────────────────┐  │ │
│  │ 📊 Theme Analysis Results                           │  │  │ Sentiment Trend     │  │ │
│  │ ┌──────────┬────────────────┬────────────┬────────┐ │  │  │ 📈 Line Graph       │  │ │
│  │ │ Theme    │ Keywords       │ Sentiment  │ Score  │ │  │  │ Week-over-week      │  │ │
│  │ ├──────────┼────────────────┼────────────┼────────┤ │  │  └─────────────────────┘  │ │
│  │ │ 🔴 Login │ "login"...     │ Negative   │ 0.85   │ │  │                           │ │
│  │ │ 🟢 Ret   │ "returns"...   │ Positive   │ 0.72   │ │  │  ┌─────────────────────┐  │ │
│  │ │ 🟡 Fees  │ "charges"...   │ Mixed      │ 0.65   │ │  │  │ Mention Volume      │  │ │
│  │ └──────────┴────────────────┴────────────┴────────┘ │  │  │ 📊 Bar Chart        │  │ │
│  └─────────────────────────────────────────────────────┘  │  │ 42 Login, 28 Ret    │  │ │
│                                                           │  └─────────────────────┘  │ │
│  ┌─────────────────────────────────────────────────────┐  │  ┌─────────────────────┐  │ │
│  │ 📈 Weekly Product Pulse (Generated)                  │  │  │ Top Keywords Cloud  │  │ │
│  │                                                     │  │  │ ☁️ Word Cloud       │  │ │
│  │ This week, customers are primarily concerned with   │  │  │ login, returns,     │  │ │
│  │ login issues (42 mentions), followed by positive   │  │  │ password, charges   │  │ │
│  │ feedback on returns (28 mentions).                 │  │  └─────────────────────┘  │ │
│  │                                                     │  │                           │ │
│  │ 🎯 Action Ideas:                                   │  │  [📊 View Full Report]    │ │
│  │ 1. Improve login error messaging                   │  │                           │ │
│  │ 2. Add password reset tutorial                     │  └───────────────────────────┘ │
│  │ 3. Create returns walkthrough video                │                                  │
│  │                                                     │                                  │
│  │ 📅 Generated: 2024-01-15 | Word Count: 235         │                                  │
│  └─────────────────────────────────────────────────────┘                                  │
│                                                                                           │
│  ┌─────────────────────────────────────────────────────────────────────────────────────┐  │
│  │ 🔗 Cross-Pillar Status                                                               │  │
│  │ Top Theme: "Login Issues" (Confidence: 0.85)                                        │  │
│  │ Voice Agent Integration: ✅ Greeting will mention login help                      │  │
│  │ Pulse Doc Updated: ✅ Booking codes appended                                         │  │
│  └─────────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                           │
└───────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Voice Agent & Booking UI

> **Note**: This is the **content component** that renders in the main area when "🎙️ Voice Agent & Booking" is selected from the sidebar (Section 0).

### Design Theme

**Background**: Light Blue (#E8F4FC) - Professional, clean, easy on the eyes
**Primary Color**: Navy Blue (#1E3A5F) - Headers and key elements
**Accent Color**: Sky Blue (#5DADE2) - Interactive elements and highlights
**Text**: Dark Slate (#2C3E50) - High contrast for readability
**Cards**: White (#FFFFFF) with subtle shadow - Clean content containers

### Quick Use Tips

> 💡 **Tip**: Press and hold the microphone button to speak with the AI Voice Agent. Release to send your message. Toggle to ⌨️ Text Mode to type your message instead.
> 
> 💡 **Tip**: The Conversation Chatbot shows: 🎤 Voice input (with STT transcription), ⌨️ Text input, and 🔊 Agent responses (with TTS playback option).
> 
> 💡 **Tip**: After booking confirmation, the booking code is automatically logged to Google Docs and appears in Weekly Pulse notes.

### Wireframe Layout

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────┐
│  🎙️ PILLAR C: AI VOICE SCHEDULER                    [BG: #E8F4FC]                                   │
├─────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                       │
│                              🔧 PIPELINE STATUS                                                       │
│                                                                                                       │
│                   ⚪   🟡   🟡   🟢   🟢   🟢   🟢                                                 │
│                   VAD › STT › LLM › TTS › Calendar › Doc › Email                                    │
│                   Idle Active Active Done   Done   Done   Done                                        │
│                                                                                                       │
│  ┌───────────────────────────────┐   ┌───────────────────────────────┐   ┌───────────────────────────────┐
│  │ 🎤 VOICE RECORDING            │   │ 💬 CONVERSATION CHATBOT         │   │ ✅ BOOKING CONFIRMED          │
│  │                               │   │                               │   │                               │
│  │ ┌─────────────────────────────┐│   │ [🎙️ Voice] [⌨️ Text] Toggle    │   │ 📅 Date: Jan 16, 2024         │
│  │ │                             ││   │ ─────────────────────────────  │   │    10:30 AM                   │
│  │ │      🎤                     ││   │                               │   │                               │
│  │ │                             ││   │ 👤 You: "Schedule meeting"   │   │ 🎫 Code: MTG-2024-001         │
│  │ │   Hold to                   ││   │     🎤 STT → [transcribed]   │   │                               │
│  │ │   Record                    ││   │                               │   │ 🔗 Meet: [Open Link →]        │
│  │ │                             ││   │ 🤖 Agent: "Morning/evening?" │   │                               │
│  │ │   (Press & Hold)            ││   │     🔊 TTS → [playing...]    │   │ 📧 Email: ✓ Sent               │
│  │ │                             ││   │                               │   │                               │
│  │ └─────────────────────────────┘│   │ 👤 You: "Morning"            │   │ 📄 Docs: ✓ Logged            │
│  │                               ││   │     ⌨️ Text                  │   │                               │
│  │ ┌─────────────────────────────┐│   │                               │   │ [📋 Copy] [🔗 Meet] [📧 View] │
│  │ │  Controls:                  ││   │ 🤖 Agent: "Slots: 9,10,11AM" │   │                               │
│  │ │  [🔴 Rec] [▶️ Play] [✗ Cancel]││   │     🔊 TTS                   │   │                               │
│  │ └─────────────────────────────┘│   │                               │   │                               │
│  │                               ││   │ ─────────────────────────────  │   │                               │
│  │ ┌─────────────────────────────┐│   │ 💬 Type message... [🎤][➤]   │   │                               │
│  │ │ 🔊 AGENT VOICE OUTPUT       ││   │                               │   │                               │
│  │ │                             ││   │                               │   │                               │
│  │ │ 🤖 "Here are your            ││   │                               │   │                               │
│  │ │     available slots..."     ││   │                               │   │                               │
│  │ │                             ││   │                               │   │                               │
│  │ │ [▶️ Play Voice] [📄 Text]    ││   │                               │   │                               │
│  │ │ 🔊 TTS Processing...        ││   │                               │   │                               │
│  │ └─────────────────────────────┘│   │                               │   │                               │
│  │                               │   │                               │   │                               │
│  └───────────────────────────────┘   └───────────────────────────────┘   └───────────────────────────────┘
│                                                                                                       │
└─────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Implementation - Voice Recorder

**Option A: React**
```jsx
const VoiceRecorder = ({ onAudioCaptured }) => {
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorder = useRef(null);
  const audioChunks = useRef([]);

  const startRecording = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder.current = new MediaRecorder(stream);
    
    mediaRecorder.current.ondataavailable = (event) => {
      audioChunks.current.push(event.data);
    };
    
    mediaRecorder.current.onstop = () => {
      const audioBlob = new Blob(audioChunks.current, { type: 'audio/wav' });
      onAudioCaptured(audioBlob);
      audioChunks.current = [];
    };
    
    mediaRecorder.current.start();
    setIsRecording(true);
  };

  const stopRecording = () => {
    mediaRecorder.current.stop();
    setIsRecording(false);
  };

  return (
    <div className="voice-recorder">
      <button
        onMouseDown={startRecording}
        onMouseUp={stopRecording}
        className={`record-btn ${isRecording ? 'recording' : ''}`}
      >
        {isRecording ? '🔴 Recording...' : '🎤 Hold to Speak'}
      </button>
    </div>
  );
};
```

**Option C: Vanilla JS**
```javascript
class VoiceRecorder {
  constructor(onAudioCaptured) {
    this.onAudioCaptured = onAudioCaptured;
    this.init();
  }

  init() {
    const btn = document.getElementById('recordBtn');
    btn.addEventListener('mousedown', () => this.start());
    btn.addEventListener('mouseup', () => this.stop());
  }

  async start() {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    this.mediaRecorder = new MediaRecorder(stream);
    this.audioChunks = [];
    
    this.mediaRecorder.ondataavailable = (e) => this.audioChunks.push(e.data);
    this.mediaRecorder.onstop = () => {
      const blob = new Blob(this.audioChunks, { type: 'audio/wav' });
      this.onAudioCaptured(blob);
    };
    
    this.mediaRecorder.start();
    document.getElementById('recordBtn').classList.add('recording');
  }

  stop() {
    if (this.mediaRecorder) {
      this.mediaRecorder.stop();
      document.getElementById('recordBtn').classList.remove('recording');
    }
  }
}
```

### Implementation - Chat Messages

**Option A: React**
```jsx
const ChatMessage = ({ role, text, audioUrl }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const audioRef = useRef(null);

  const togglePlay = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  return (
    <div className={`chat-message ${role}`}>
      <div className="message-header">
        {role === 'user' ? '👤 You' : '🤖 Agent'}
      </div>
      <div className={`message-bubble ${role}`}>
        {text}
      </div>
      {audioUrl && (
        <div className="voice-controls">
          <button onClick={togglePlay} className="play-btn">
            {isPlaying ? '⏸️' : '▶️'}
          </button>
          <span className="voice-label">🔊 Voice available</span>
          <audio ref={audioRef} src={audioUrl} onEnded={() => setIsPlaying(false)} />
        </div>
      )}
    </div>
  );
};
```

---

## 5. HITL Approval Center

> **Note**: This is the **content component** that renders in the main area when "⚙️ HITL Approval Center" is selected from the sidebar (Section 0).

### Design Theme

**Background**: Light Blue (#E8F4FC) - Professional, clean, easy on the eyes
**Primary Color**: Navy Blue (#1E3A5F) - Headers and key elements
**Accent Color**: Sky Blue (#5DADE2) - Interactive elements and highlights
**Text**: Dark Slate (#2C3E50) - High contrast for readability
**Cards**: White (#FFFFFF) with subtle shadow - Clean content containers

### Quick Use Tips

> 💡 **Tip**: Review pending MCP actions (Calendar Holds and Email Drafts) before approving. Each action shows booking code and market context.
> 
> 💡 **Tip**: Click on 📄 Doc: [pulse-tracking] link to view the appended booking details in Google Docs for each action.
> 
> 💡 **Tip**: Use [✓ Approve All] to batch approve multiple actions, or review individually for sensitive requests.

### Wireframe Layout

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────┐
│  👤 HUMAN-IN-THE-LOOP APPROVAL CENTER               [BG: #E8F4FC]                                   │
├─────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   ┌─────────────────────────────┐ │
│  │ ⏳ Pending MCP Actions (3)                                    │   │ ✉️ PREVIEW DRAFT EMAIL       │ │
│  │                                                             │   │                             │ │
│  │ ┌──────────┬────────────────┬───────────────┬──────────────┐│   │ Selected: MTG-2024-001      │ │
│  │ │ Action   │ Booking Code   │ Details       │ Approve?     ││   │                             │ │
│  │ ├──────────┼────────────────┼───────────────┼──────────────┤│   │ ┌─────────────────────────┐ │ │
│  │ │ 📅 Cal   │ MTG-2024-001   │ Jan 16, 10:30 │ [✓]   [✗]    ││   │ │ To: advisor@example.com │ │ │
│  │ │          │                │ Advisor: John │  [👁️]       ││   │ │ From: noreply@investors │ │ │
│  │ │          │ 📄 Doc: [pulse-tracking] 🔗               │              ││   │ │ Subject: Booking Conf │ │ │
│  │ ├──────────┼────────────────┼───────────────┼──────────────┤│   │ ├─────────────────────────┤ │ │
│  │ │ ✉️ Email │ MTG-2024-001   │ To: advisor@  │ [✓]   [✗]    ││   │ │ Dear Advisor,           │ │ │
│  │ │          │                │ Context: Login│  [👁️]       ││   │ │                         │ │ │
│  │ │          │ 📄 Doc: [pulse-tracking] 🔗               │              ││   │ │ A meeting has been book │ │ │
│  │ ├──────────┼────────────────┼───────────────┼──────────────┤│   │ │ for Jan 16 at 10:30 AM. │ │ │
│  │ │ 📅 Cal   │ MTG-2024-002   │ Jan 17, 2:00  │ [✓]   [✗]    ││   │ │                         │ │ │
│  │ │          │                │ Advisor: Jane │  [👁️]       ││   │ │ Booking Code: MTG-2024  │ │ │
│  │ │          │ 📄 Doc: [pulse-tracking] 🔗               │              ││   │ │ Meet Link: [Included]   │ │ │
│  │ └──────────┴────────────────┴───────────────┴──────────────┘│   │ │                         │ │ │
│  │                                                             │   │ │ Context: Login Theme    │ │ │
│  │ [✓ Approve All]  [✗ Reject All]  [🔄 Refresh]               │   │ │                         │ │ │
│  │                                                             │   │ │ Best regards,           │ │ │
│  │                                                             │   │ │ Investor Intelligence   │ │ │
│  └─────────────────────────────────────────────────────────────┘   │ └─────────────────────────┘ │ │
│                                                                       │                             │ │
│  ┌─────────────────────────────────────────────────────────────┐   │ [✉️ Edit Draft] [📧 Send]   │ │
│  │ ✅ Approved Actions (5)                                     │   │                             │ │
│  │ ┌──────────┬────────────────┬───────────────┬──────────────┐│   └─────────────────────────────┘ │
│  │ │ 📅 Cal   │ MTG-2024-000   │ Jan 15, 9:00  │ ✅ Executed  ││                                   │
│  │ │          │ 📄 Doc: [pulse-tracking] 🔗               │              ││                                   │
│  │ │ ✉️ Email │ MTG-2024-000   │ Sent          │ ✅ Delivered ││                                   │
│  │ │          │ 📄 Doc: [pulse-tracking] 🔗               │              ││                                   │
│  │ └──────────┴────────────────┴───────────────┴──────────────┘│                                   │
│  └─────────────────────────────────────────────────────────────┘                                   │
│                                                                                                       │
└─────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Implementation

**Option A: React**
```jsx
const HITLApprovalCenter = () => {
  const [pendingActions, setPendingActions] = useState([]);

  useEffect(() => {
    fetchPendingActions();
    const interval = setInterval(fetchPendingActions, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleApprove = async (actionId) => {
    await axios.post(`/api/actions/${actionId}/approve`);
    fetchPendingActions();
  };

  const handleReject = async (actionId) => {
    await axios.post(`/api/actions/${actionId}/reject`);
    fetchPendingActions();
  };

  return (
    <div className="approval-center">
      <h2>👤 Human-in-the-Loop Approval Center</h2>
      <table className="approval-table">
        <thead>
          <tr>
            <th>Action</th>
            <th>Booking Code</th>
            <th>Details</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {pendingActions.map(action => (
            <tr key={action.id}>
              <td><strong>{action.type}</strong></td>
              <td>{action.booking_code}</td>
              <td>{action.details}</td>
              <td>
                <button onClick={() => handleApprove(action.id)} className="btn-approve">✓</button>
                <button onClick={() => handleReject(action.id)} className="btn-reject">✗</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
```

---

## 6. Pipeline Status UI

> **Note**: This is a **sub-component** used within Pillar C (Voice Agent) content to show real-time voice pipeline status.

### Wireframe Layout

```
┌─────────────────────────────────────────────────────────────────────────┐
│  🔧 PIPELINE STATUS                                                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ⚪      🟡       🟡       🟢        🟢        🟢        🟢              │
│  VAD  ›  STT  ›  LLM  ›  TTS  ›  Calendar  ›  Doc  ›  Email           │
│ Idle   Active  Active   Done    Done       Done    Done               │
│                                                                         │
│  Legend:                                                                │
│  ⚪ Gray  = Idle/Waiting    🟡 Amber = Active/Processing               │
│  🟢 Green = Done           🔴 Red   = Error                           │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Implementation

**Option A: React**
```jsx
const PipelineStatus = ({ currentStatus }) => {
  const PIPELINE_STEPS = [
    { key: 'VAD', label: 'VAD', desc: 'Voice Activity Detection' },
    { key: 'STT', label: 'STT', desc: 'Speech-to-Text' },
    { key: 'LLM', label: 'LLM', desc: 'Intent Processing' },
    { key: 'TTS', label: 'TTS', desc: 'Text-to-Speech' },
    { key: 'Calendar', label: 'Calendar', desc: 'Google Calendar' },
    { key: 'Doc', label: 'Doc', desc: 'Google Doc' },
    { key: 'Email', label: 'Email', desc: 'Email' }
  ];

  const STATUS_CONFIG = {
    idle: { color: '#6B7280', emoji: '⚪', className: 'idle' },
    active: { color: '#F59E0B', emoji: '🟡', className: 'active' },
    done: { color: '#10B981', emoji: '🟢', className: 'done' },
    error: { color: '#EF4444', emoji: '🔴', className: 'error' }
  };

  return (
    <div className="pipeline-status-container">
      <h3>🔧 Pipeline Status</h3>
      <div className="pipeline-steps">
        {PIPELINE_STEPS.map((step, index) => {
          const status = currentStatus[step.key] || 'idle';
          const config = STATUS_CONFIG[status];
          
          return (
            <div key={step.key} className={`pipeline-step ${config.className}`}>
              <div className="step-indicator" style={{ color: config.color }}>
                {config.emoji}
              </div>
              <div className="step-label">{step.label}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
```

### Self-RAG Pipeline Status (Pillar A)

```
┌─────────────────────────────────────────────────────────────────────────┐
│  🔧 SELF-RAG PIPELINE STATUS                                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ⚪      🟡        🟡        🟡        🟢        🟢        🟢              │
│ Query › Expand › Retrieve › Check  › Re-  › Generate › Output         │
│ Input   Variants  Chunks   Suffice?  trieve?  Response   JSON         │
│ Idle    Active    Active   Active    Done     Done      Done           │
│                                                                         │
│  Active Variants: "ELSS exit load", "redemption fees"                  │
│  Retrieved: 8 chunks from Pinecone (M1: 5, M1.1: 3)                   │
│  Sufficiency: ✅ Sufficient (Loop 0)                                     │
│  Model: GPT-4o-mini (reflection) → GPT-4o (generation)               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Option A: React**
```jsx
const SelfRAGPipelineStatus = ({ status, debugInfo }) => {
  const STEPS = [
    { key: 'query', label: 'Query', desc: 'User Input' },
    { key: 'expand', label: 'Expand', desc: 'Query Variants' },
    { key: 'retrieve', label: 'Retrieve', desc: 'Dense Retrieval (Pinecone)' },
    { key: 'check', label: 'Check', desc: 'Sufficiency Check (GPT-4o-mini)' },
    { key: 'reretrieve', label: 'Re-trieve', desc: 'Loop if needed' },
    { key: 'generate', label: 'Generate', desc: '6-Bullets (GPT-4o)' },
    { key: 'output', label: 'Output', desc: 'JSON Response' }
  ];

  const STATUS_CONFIG = {
    idle: { emoji: '⚪', color: '#6B7280' },
    active: { emoji: '🟡', color: '#F59E0B' },
    done: { emoji: '🟢', color: '#10B981' },
    error: { emoji: '🔴', color: '#EF4444' }
  };

  return (
    <div className="pipeline-status">
      <h3>🔧 Self-RAG Pipeline</h3>
      
      <div className="pipeline-steps">
        {STEPS.map((step, i) => {
          const s = status[step.key] || 'idle';
          const config = STATUS_CONFIG[s];
          return (
            <div key={step.key} className="step">
              <div className="step-indicator" style={{ color: config.color }}>
                {config.emoji}
              </div>
              <div className="step-label">{step.label}</div>
              <div className="step-desc">{step.desc}</div>
            </div>
          );
        })}
      </div>

      {/* Debug Info */}
      {debugInfo && (
        <div className="debug-info">
          <p><strong>Variants:</strong> {debugInfo.variants?.join(', ')}</p>
          <p><strong>Retrieved:</strong> {debugInfo.chunkCount} chunks</p>
          <p><strong>Sufficiency:</strong> {debugInfo.sufficient ? '✅' : '❌'} (Loop {debugInfo.loopCount})</p>
          <p><strong>Models:</strong> GPT-4o-mini → GPT-4o via OpenRouter</p>
        </div>
      )}
    </div>
  );
};
```

---

## 7. Cross-Cutting Components

> **Note**: These are **shared components/styles** used across all pillar content components within the unified dashboard.

### Common CSS Styles

```css
/* common.css - Shared styles for all pillars */

/* Layout */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

/* Cards */
.card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

/* Buttons */
.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 12px 24px;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}

/* Loading States */
.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: #666;
}

.spinner {
  border: 3px solid #f3f3f3;
  border-top: 3px solid #667eea;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Status Badges */
.badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
}

.badge-success { background: #e8f5e9; color: #2e7d32; }
.badge-warning { background: #fff3e0; color: #ef6c00; }
.badge-error { background: #ffebee; color: #c62828; }
.badge-info { background: #e3f2fd; color: #1565c0; }

/* Responsive */
@media (max-width: 768px) {
  .container {
    padding: 10px;
  }
  
  .card {
    padding: 16px;
  }
}
```

### Unified Dashboard Layout

```
┌─────────────────────────────────────────────────────────────────────────┐
│  🏛️ INVESTOR OPS & INTELLIGENCE SUITE                    [User] [⚙️]   │
├─────────────────────────────────────────────────────────────────────────┤
│  [📊 Pillar A]  [📈 Pillar B]  [🎙️ Pillar C]  [📋 Evals]  [👤 HITL]     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│                    [ACTIVE PILLAR CONTENT AREA]                          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Navigation Component

**React**
```jsx
const Navigation = ({ activePillar, onPillarChange }) => {
  const pillars = [
    { id: 'A', name: '📊 Pillar A', label: 'Knowledge Base' },
    { id: 'B', name: '📈 Pillar B', label: 'Weekly Pulse' },
    { id: 'C', name: '🎙️ Pillar C', label: 'Voice Agent' },
    { id: 'evals', name: '📋 Evals', label: 'Evaluation' },
    { id: 'hitl', name: '👤 HITL', label: 'Approvals' }
  ];

  return (
    <nav className="nav-tabs">
      {pillars.map(pillar => (
        <button
          key={pillar.id}
          className={`nav-tab ${activePillar === pillar.id ? 'active' : ''}`}
          onClick={() => onPillarChange(pillar.id)}
        >
          <span className="nav-name">{pillar.name}</span>
          <span className="nav-label">{pillar.label}</span>
        </button>
      ))}
    </nav>
  );
};
```

**Vanilla JS**
```javascript
class Navigation {
  constructor(containerId, onPillarChange) {
    this.container = document.getElementById(containerId);
    this.onPillarChange = onPillarChange;
    this.pillars = [
      { id: 'A', name: '📊 Pillar A', label: 'Knowledge Base' },
      { id: 'B', name: '📈 Pillar B', label: 'Weekly Pulse' },
      { id: 'C', name: '🎙️ Pillar C', label: 'Voice Agent' },
      { id: 'evals', name: '📋 Evals', label: 'Evaluation' },
      { id: 'hitl', name: '👤 HITL', label: 'Approvals' }
    ];
    this.activePillar = 'A';
    this.render();
  }

  render() {
    const buttons = this.pillars.map(pillar => `
      <button 
        class="nav-tab ${this.activePillar === pillar.id ? 'active' : ''}"
        data-pillar="${pillar.id}"
      >
        <span class="nav-name">${pillar.name}</span>
        <span class="nav-label">${pillar.label}</span>
      </button>
    `).join('');

    this.container.innerHTML = `<nav class="nav-tabs">${buttons}</nav>`;
    
    this.container.querySelectorAll('.nav-tab').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const pillarId = e.currentTarget.dataset.pillar;
        this.setActivePillar(pillarId);
      });
    });
  }

  setActivePillar(pillarId) {
    this.activePillar = pillarId;
    this.render();
    this.onPillarChange(pillarId);
  }
}
```

---

**Document Version**: 1.0  
**Last Updated**: April 2026  
**Related Documents**: 
- For backend implementation: [architecture.md](architecture.md)
- For MCP integration: [mcpIntegration.md](mcpIntegration.md)
- For voice agent details: [voiceAgent.md](voiceAgent.md)
- For RAG details: [rag.md](rag.md)
- For theme classification: [themeClassification.md](themeClassification.md)
- For safety/compliance: [rules.md](rules.md)
- For edge cases: [edgeCase.md](edgeCase.md)
- For evaluation: [evals.md](evals.md)

---

## Footer

© 2026 All rights reserved [Ashish Kumar Sankhua](../LICENSE)

**License**: [MIT License](../LICENSE) - Click to view full license terms
