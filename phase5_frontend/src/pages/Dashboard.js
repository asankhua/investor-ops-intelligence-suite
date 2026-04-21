import React from 'react';
import { useQuery } from 'react-query';
import styled from 'styled-components';
import { BookOpen, BarChart3, Mic, Settings, Activity, Database, TrendingUp, AlertCircle } from 'lucide-react';
import { dashboardAPI, pillarBAPI } from '../services/api';

const Container = styled.div`
  max-width: 1400px;
  margin: 0 auto;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
`;

const Title = styled.h1`
  color: #1E3A5F;
  font-size: 28px;
  font-weight: 600;
`;

const UserInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 10px;
  color: #1E3A5F;
  font-weight: 500;
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 30px;
`;

const StatCard = styled.div`
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(30, 58, 95, 0.08);
  display: flex;
  align-items: center;
  gap: 16px;
`;

const StatIcon = styled.div`
  width: 56px;
  height: 56px;
  border-radius: 12px;
  background: ${props => props.bg || '#E8F4FC'};
  display: flex;
  align-items: center;
  justify-content: center;
  color: ${props => props.color || '#1E3A5F'};
`;

const StatContent = styled.div`
  flex: 1;
`;

const StatValue = styled.div`
  font-size: 32px;
  font-weight: 700;
  color: #1E3A5F;
  line-height: 1;
`;

const StatLabel = styled.div`
  font-size: 14px;
  color: #5DADE2;
  margin-top: 4px;
`;

const PillarCardsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 30px;
`;

const PillarCard = styled.div`
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(30, 58, 95, 0.08);
  border-left: 4px solid ${props => props.borderColor || '#5DADE2'};
  transition: transform 0.2s ease;
  cursor: pointer;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 4px 16px rgba(30, 58, 95, 0.12);
  }
`;

const PillarHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
`;

const PillarIcon = styled.div`
  width: 48px;
  height: 48px;
  border-radius: 10px;
  background: ${props => props.bg || '#E8F4FC'};
  display: flex;
  align-items: center;
  justify-content: center;
  color: ${props => props.color || '#1E3A5F'};
`;

const PillarTitle = styled.h3`
  color: #1E3A5F;
  font-size: 18px;
  font-weight: 600;
  margin: 0;
`;

const PillarSubtitle = styled.p`
  color: #5DADE2;
  font-size: 13px;
  margin: 4px 0 0 0;
`;

const PillarStats = styled.div`
  display: flex;
  gap: 20px;
  margin-top: 16px;
`;

const PillarStat = styled.div`
  text-align: center;
`;

const PillarStatValue = styled.div`
  font-size: 20px;
  font-weight: 700;
  color: #1E3A5F;
`;

const PillarStatLabel = styled.div`
  font-size: 12px;
  color: #5DADE2;
`;

const ActivitySection = styled.div`
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(30, 58, 95, 0.08);
`;

const SectionHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
`;

const SectionTitle = styled.h2`
  color: #1E3A5F;
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const LastSynced = styled.span`
  font-size: 12px;
  color: #5DADE2;
`;

const ActivityList = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 12px;
`;

const ActivityItem = styled.div`
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  background: #F8FBFD;
  border: 1px solid #E8F4FC;
`;

const ActivityIcon = styled.div`
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: ${props => props.bg || '#E8F4FC'};
  display: flex;
  align-items: center;
  justify-content: center;
  color: ${props => props.color || '#1E3A5F'};
  font-size: 14px;
`;

const ActivityContent = styled.div`
  width: 100%;
`;

const ActivityText = styled.p`
  color: #1E3A5F;
  font-size: 14px;
  margin: 0;
  min-height: 42px;
`;

const ActivityTime = styled.span`
  color: #5DADE2;
  font-size: 12px;
  display: inline-block;
  margin-top: 8px;
`;

const PerformanceBadge = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  background: ${props => props.status === 'operational' ? '#E8F8F0' : '#FDF2E9'};
  color: ${props => props.status === 'operational' ? '#27AE60' : '#E67E22'};
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
`;

const QuickTips = styled.div`
  background: linear-gradient(135deg, #1E3A5F 0%, #2a4a73 100%);
  border-radius: 12px;
  padding: 20px;
  margin-top: 20px;
  color: white;
`;

const QuickTipsTitle = styled.h4`
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #5DADE2;
`;

const QuickTip = styled.p`
  margin: 4px 0;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.9);
  &::before {
    content: '💡 ';
  }
`;

const Dashboard = () => {
  const { data: stats, isLoading: statsLoading, isError: statsError } = useQuery(
    'dashboardStats',
    async () => (await dashboardAPI.getStats()).data,
    { refetchInterval: 15000 }
  );

  const { data: pillars, isLoading: pillarsLoading, isError: pillarsError } = useQuery(
    'dashboardPillars',
    async () => (await dashboardAPI.getPillars()).data?.pillars || [],
    { refetchInterval: 15000 }
  );

  const { data: performance, isLoading: performanceLoading, isError: performanceError } = useQuery(
    'dashboardPerformance',
    async () => (await dashboardAPI.getPerformance()).data,
    { refetchInterval: 15000 }
  );

  const { data: activities, isLoading: activitiesLoading, isError: activitiesError } = useQuery(
    'dashboardActivity',
    async () => (await dashboardAPI.getActivity()).data?.activity || [],
    { refetchInterval: 15000 }
  );

  const { data: pulseData } = useQuery(
    'dashboardPulse',
    async () => (await pillarBAPI.getWeeklyPulse()).data,
    { refetchInterval: 60000 }
  );

  if (statsLoading || pillarsLoading || performanceLoading || activitiesLoading) {
    return (
      <Container>
        <Title>Loading dashboard data...</Title>
      </Container>
    );
  }

  if (statsError || pillarsError || performanceError || activitiesError) {
    return (
      <Container>
        <Title>Unable to fetch live dashboard data. Check Phase 4 gateway.</Title>
      </Container>
    );
  }

  const lastSynced = stats?.last_synced ? new Date(stats.last_synced).toLocaleString() : 'n/a';

  return (
    <Container>
      <Header>
        <Title>Investor Ops & Intelligence Suite</Title>
        <UserInfo>
          <PerformanceBadge status={performance?.status}>
            <Activity size={16} />
            {performance?.score ?? 0}% Operational
          </PerformanceBadge>
          <span>👤 Live View</span>
        </UserInfo>
      </Header>

      <StatsGrid>
        <StatCard>
          <StatIcon bg="#E8F4FC" color="#1E3A5F"><Database size={28} /></StatIcon>
          <StatContent>
            <StatValue>{stats?.kb_docs?.toLocaleString()}</StatValue>
            <StatLabel>KB Documents</StatLabel>
          </StatContent>
        </StatCard>
        <StatCard>
          <StatIcon bg="#F0E8FC" color="#6B4EE6"><BarChart3 size={28} /></StatIcon>
          <StatContent>
            <StatValue>{stats?.themes_active}</StatValue>
            <StatLabel>Active Themes</StatLabel>
          </StatContent>
        </StatCard>
        <StatCard>
          <StatIcon bg="#E8FCF0" color="#27AE60"><Mic size={28} /></StatIcon>
          <StatContent>
            <StatValue>{stats?.bookings_this_week}</StatValue>
            <StatLabel>Weekly Bookings</StatLabel>
          </StatContent>
        </StatCard>
        <StatCard>
          <StatIcon bg="#FCE8E8" color="#E74C3C"><AlertCircle size={28} /></StatIcon>
          <StatContent>
            <StatValue>{stats?.pending_approvals}</StatValue>
            <StatLabel>Pending Approvals</StatLabel>
          </StatContent>
        </StatCard>
      </StatsGrid>

      <PillarCardsGrid>
        <PillarCard borderColor="#5DADE2">
          <PillarHeader>
            <PillarIcon bg="#E8F4FC" color="#1E3A5F"><BookOpen size={24} /></PillarIcon>
            <div>
              <PillarTitle>Smart-Sync Knowledge Base</PillarTitle>
              <PillarSubtitle>Self-RAG Knowledge Base</PillarSubtitle>
            </div>
          </PillarHeader>
          <PillarStats>
            <PillarStat>
              <PillarStatValue>{stats?.kb_docs?.toLocaleString?.() || 0}</PillarStatValue>
              <PillarStatLabel>Documents</PillarStatLabel>
            </PillarStat>
            <PillarStat>
              <PillarStatValue>{pillars?.find((p) => p.pillar === 'A')?.status === 'operational' ? 'Live' : 'Down'}</PillarStatValue>
              <PillarStatLabel>Status</PillarStatLabel>
            </PillarStat>
            <PillarStat>
              <PillarStatValue style={{ color: '#27AE60' }}>{pillars?.find((p) => p.pillar === 'A')?.name || 'RAG'}</PillarStatValue>
              <PillarStatLabel>Engine</PillarStatLabel>
            </PillarStat>
          </PillarStats>
        </PillarCard>

        <PillarCard borderColor="#6B4EE6">
          <PillarHeader>
            <PillarIcon bg="#F0E8FC" color="#6B4EE6"><BarChart3 size={24} /></PillarIcon>
            <div>
              <PillarTitle>Insight-Driven Pulse</PillarTitle>
              <PillarSubtitle>Weekly Theme Analysis</PillarSubtitle>
            </div>
          </PillarHeader>
          <PillarStats>
            <PillarStat>
              <PillarStatValue>{stats?.themes_active ?? 0}</PillarStatValue>
              <PillarStatLabel>Themes</PillarStatLabel>
            </PillarStat>
            <PillarStat>
              <PillarStatValue>{pillars?.find((p) => p.pillar === 'B')?.status === 'operational' ? 'Live' : 'Down'}</PillarStatValue>
              <PillarStatLabel>Status</PillarStatLabel>
            </PillarStat>
            <PillarStat>
              <PillarStatValue style={{ color: pulseData?.sentiment_score < 0 ? '#E74C3C' : '#27AE60' }}>
                {pulseData?.sentiment_score !== undefined ? pulseData.sentiment_score.toFixed(2) : 'N/A'}
              </PillarStatValue>
              <PillarStatLabel>Sentiment</PillarStatLabel>
            </PillarStat>
          </PillarStats>
        </PillarCard>

        <PillarCard borderColor="#27AE60">
          <PillarHeader>
            <PillarIcon bg="#E8FCF0" color="#27AE60"><Mic size={24} /></PillarIcon>
            <div>
              <PillarTitle>AI Voice Scheduler</PillarTitle>
              <PillarSubtitle>Voice-Based Booking</PillarSubtitle>
            </div>
          </PillarHeader>
          <PillarStats>
            <PillarStat>
              <PillarStatValue>{stats?.bookings_this_week ?? 0}</PillarStatValue>
              <PillarStatLabel>Bookings</PillarStatLabel>
            </PillarStat>
            <PillarStat>
              <PillarStatValue>{pillars?.find((p) => p.pillar === 'C')?.status === 'operational' ? 'Live' : 'Down'}</PillarStatValue>
              <PillarStatLabel>Status</PillarStatLabel>
            </PillarStat>
            <PillarStat>
              <PillarStatValue style={{ color: stats?.pending_approvals > 0 ? '#E67E22' : '#27AE60' }}>
                {stats?.pending_approvals ?? 0}
              </PillarStatValue>
              <PillarStatLabel>Pending</PillarStatLabel>
            </PillarStat>
          </PillarStats>
        </PillarCard>
      </PillarCardsGrid>

      <ActivitySection>
        <SectionHeader>
          <SectionTitle>
            <Activity size={20} />
            Recent Activity
          </SectionTitle>
          <LastSynced>Last synced: {lastSynced}</LastSynced>
        </SectionHeader>
        <ActivityList>
          {(activities || []).slice(0, 5).map((activity, index) => (
            <ActivityItem key={index}>
              <ActivityIcon 
                bg={activity.type === 'state_sync' ? '#E8FCF0' : '#E8F4FC'}
                color={activity.type === 'state_sync' ? '#27AE60' : '#1E3A5F'}
              >
                {activity.type === 'state_sync' ? '🔗' : '📌'}
              </ActivityIcon>
              <ActivityContent>
                <ActivityText>{activity.message}</ActivityText>
                <ActivityTime>{activity.time ? new Date(activity.time).toLocaleString() : 'n/a'}</ActivityTime>
              </ActivityContent>
            </ActivityItem>
          ))}
          {(!activities || activities.length === 0) && (
            <ActivityItem>
              <ActivityContent>
                <ActivityText>No live activity events yet.</ActivityText>
                <ActivityTime>Trigger booking/pulse actions to populate this feed.</ActivityTime>
              </ActivityContent>
            </ActivityItem>
          )}
        </ActivityList>
      </ActivitySection>

      <QuickTips>
        <QuickTipsTitle>Quick Use Tips</QuickTipsTitle>
        <QuickTip>Click 📊 in sidebar to search Knowledge Base with Self-RAG</QuickTip>
        <QuickTip>Click 📈 in sidebar to view Weekly Pulse with theme analysis</QuickTip>
        <QuickTip>Click 🎙️ in sidebar to start voice booking with pipeline tracking</QuickTip>
        <QuickTip>Click ⚙️ in sidebar to approve pending HITL actions</QuickTip>
      </QuickTips>
    </Container>
  );
};

export default Dashboard;
