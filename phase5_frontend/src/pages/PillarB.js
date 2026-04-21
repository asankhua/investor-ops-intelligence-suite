import React, { useState, useEffect } from 'react';
import { useQuery } from 'react-query';
import styled from 'styled-components';
import { BarChart3, RefreshCw, Download, Clock } from 'lucide-react';
import { XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell, Legend } from 'recharts';
import { pillarBAPI } from '../services/api';

const DONUT_COLORS = ['#1E3A5F', '#5DADE2', '#6B4EE6', '#27AE60', '#E67E22', '#E74C3C'];

const Container = styled.div`
  max-width: 1600px;
  margin: 0 auto;
  min-height: calc(100vh - 40px);
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 2px solid #E8F4FC;
`;

const Title = styled.h1`
  color: #1E3A5F;
  font-size: 24px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 12px;
`;

const HeaderActions = styled.div`
  display: flex;
  gap: 12px;
  align-items: center;
`;

const Button = styled.button`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  background: ${props => props.variant === 'secondary' ? '#5DADE2' : '#1E3A5F'};
  color: white;
  
  &:hover {
    opacity: 0.9;
    transform: translateY(-1px);
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

const LastSynced = styled.span`
  font-size: 13px;
  color: #5DADE2;
  display: flex;
  align-items: center;
  gap: 6px;
`;

const MainLayout = styled.div`
  display: grid;
  grid-template-columns: 1fr 380px;
  gap: 24px;
`;

const LeftColumn = styled.div`
  display: flex;
  flex-direction: column;
  gap: 24px;
`;

const RightColumn = styled.div`
  display: flex;
  flex-direction: column;
  gap: 24px;
`;

const Card = styled.div`
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(30, 58, 95, 0.08);
  padding: 24px;
`;

const CardHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
`;

const CardTitle = styled.h2`
  color: #1E3A5F;
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const WeeklyPulseHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
`;

const WeekInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`;

const WeekBadge = styled.div`
  background: #E8F4FC;
  color: #1E3A5F;
  padding: 8px 16px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 14px;
`;

const ThemesContainer = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
  margin-bottom: 20px;
`;

const ThemeCard = styled.div`
  background: ${props => props.selected ? '#E8F4FC' : '#F8FBFD'};
  border: 2px solid ${props => props.selected ? '#5DADE2' : 'transparent'};
  border-radius: 10px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s;
  
  &:hover {
    background: #E8F4FC;
  }
`;

const ConfidenceBadge = styled.span`
  background: ${props => props.confidence > 0.8 ? '#E8FCF0' : props.confidence > 0.5 ? '#FDF2E9' : '#FCE8E8'};
  color: ${props => props.confidence > 0.8 ? '#27AE60' : props.confidence > 0.5 ? '#E67E22' : '#E74C3C'};
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
`;

const SummaryText = styled.p`
  color: #1E3A5F;
  font-size: 15px;
  line-height: 1.8;
  margin-bottom: 20px;
`;

const ActionsSection = styled.div`
  background: #F8FBFD;
  border-radius: 8px;
  padding: 20px;
`;

const ActionsTitle = styled.h4`
  color: #1E3A5F;
  font-size: 14px;
  margin: 0 0 16px 0;
`;

const ActionList = styled.ul`
  list-style: none;
  padding: 0;
  margin: 0;
`;

const ActionItem = styled.li`
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid #E8F4FC;
  
  &:last-child {
    border-bottom: none;
  }
`;

const ActionNumber = styled.span`
  width: 24px;
  height: 24px;
  background: #5DADE2;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
`;

const ActionText = styled.span`
  color: #1E3A5F;
  font-size: 14px;
  line-height: 1.5;
`;

const ThemeHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
`;

const ThemeName = styled.h4`
  color: #1E3A5F;
  font-size: 15px;
  font-weight: 600;
  margin: 0;
`;

const ThemeMeta = styled.div`
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #5DADE2;
`;

const ChartContainer = styled.div`
  height: 200px;
  margin-top: 16px;
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 20px;
`;

const StatBox = styled.div`
  background: #F8FBFD;
  border-radius: 8px;
  padding: 16px;
  text-align: center;
`;

const StatValue = styled.div`
  font-size: 28px;
  font-weight: 700;
  color: #1E3A5F;
  margin-bottom: 4px;
`;

const StatLabel = styled.div`
  font-size: 12px;
  color: #5DADE2;
`;

const SentimentBar = styled.div`
  display: flex;
  height: 32px;
  border-radius: 16px;
  overflow: hidden;
  margin-top: 12px;
`;

const SentimentSegment = styled.div`
  background: ${props => props.type === 'positive' ? '#27AE60' : props.type === 'neutral' ? '#F39C12' : '#E74C3C'};
  width: ${props => props.percentage}%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 12px;
  font-weight: 500;
`;

const KeywordsCloud = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
`;

const Keyword = styled.span`
  background: ${props => props.size === 'large' ? '#1E3A5F' : props.size === 'medium' ? '#5DADE2' : '#E8F4FC'};
  color: ${props => props.size === 'large' || props.size === 'medium' ? 'white' : '#1E3A5F'};
  padding: 6px 12px;
  border-radius: 16px;
  font-size: ${props => props.size === 'large' ? '14px' : props.size === 'medium' ? '13px' : '12px'};
  font-weight: ${props => props.size === 'large' ? '600' : '400'};
`;

const KeywordLabel = styled.span`
  margin-right: 6px;
`;

const KeywordCount = styled.span`
  background: rgba(255, 255, 255, 0.22);
  border-radius: 10px;
  padding: 2px 6px;
  font-size: 11px;
`;

const QuickTips = styled.div`
  background: #1E3A5F;
  border-radius: 12px;
  padding: 20px;
  color: white;
  margin-top: 24px;
`;

const QuickTipsTitle = styled.h4`
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #5DADE2;
`;

const QuickTip = styled.p`
  margin: 6px 0;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.9);
  &::before {
    content: '💡 ';
  }
`;

const VolumeChart = styled.div`
  height: 180px;
  margin-top: 16px;
`;

const StateCard = styled(Card)`
  text-align: center;
  color: #1E3A5F;
`;

const PillarB = () => {
  const [selectedTheme, setSelectedTheme] = useState('');
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);

  const { data: pulseData, isLoading: pulseLoading, isError: pulseError, error: pulseErrorData, refetch: refetchPulse } = useQuery(
    'pillarBPulse',
    async () => (await pillarBAPI.getWeeklyPulse()).data
  );

  const { data: analyticsData, isLoading: analyticsLoading, isError: analyticsError, error: analyticsErrorData, refetch: refetchAnalytics } = useQuery(
    'pillarBAnalytics',
    async () => (await pillarBAPI.getAnalytics()).data
  );

  const themeNames = (pulseData?.top_themes || []).map((theme) => theme.theme);

  useEffect(() => {
    if (!selectedTheme && themeNames.length > 0) {
      setSelectedTheme(themeNames[0]);
    }
  }, [themeNames, selectedTheme]);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      await pillarBAPI.refreshAnalysis();
      await Promise.all([refetchPulse(), refetchAnalytics()]);
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleDownload = async () => {
    setIsDownloading(true);
    try {
      const response = await pillarBAPI.downloadReviewsCSV();
      const blob = new Blob([response.data], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'reviews-latest.csv';
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } finally {
      setIsDownloading(false);
    }
  };

  if (pulseLoading || analyticsLoading) {
    return (
      <Container>
        <StateCard>
          <CardTitle>Loading Weekly Pulse...</CardTitle>
        </StateCard>
      </Container>
    );
  }

  if (pulseError || analyticsError) {
    return (
      <Container>
        <StateCard>
          <CardTitle>Failed to load Weekly Pulse</CardTitle>
          <p style={{ color: '#5DADE2', marginTop: '8px' }}>
            {pulseErrorData?.response?.data?.detail || analyticsErrorData?.response?.data?.detail || 'Backend did not return valid Phase 2 data.'}
          </p>
        </StateCard>
      </Container>
    );
  }

  if (!pulseData || !analyticsData) {
    return (
      <Container>
        <StateCard>
          <CardTitle>No Weekly Pulse Data</CardTitle>
          <p style={{ color: '#5DADE2', marginTop: '8px' }}>
            Phase 2 did not return a pulse payload.
          </p>
        </StateCard>
      </Container>
    );
  }

  const themes = (pulseData.top_themes || []).map((theme) => ({
    name: theme.theme,
    confidence: Number(theme.confidence || 0),
    mentions: Number(theme.mention_count || 0),
    trend: '',
    sentiment: Number(theme.sentiment_score || 0),
  }));

  const weeklyPulse = {
    week: `Generated ${new Date(pulseData.generated_at).toLocaleString()}`,
    summary: pulseData.summary,
    actions: pulseData.action_ideas
  };

  const mentionVolumeData = (analyticsData.mention_volume || []).map((x) => ({
    label: x.theme,
    count: Number(x.count || 0),
  }));

  const themeDistributionData = (analyticsData.theme_distribution || []).map((x) => ({
    name: x.theme,
    value: Number(x.count || 0),
    percentage: Number(x.percentage || 0),
  }));

  const sentimentTrendData = (analyticsData.sentiment_trends || []).map((x) => ({
    date: x.date,
    score: Number(x.score || 0),
  }));

  const totalMentions = themeDistributionData.reduce((sum, row) => sum + row.value, 0);
  const avgConfidence = themes.length
    ? themes.reduce((sum, row) => sum + row.confidence, 0) / themes.length
    : 0;

  const keywords = (analyticsData.keywords || []).slice(0, 12).map((kw, index) => ({
    word: kw.word,
    size: index < 4 ? 'large' : index < 8 ? 'medium' : 'small',
    count: kw.frequency,
  }));

  return (
    <Container>
      <Header>
        <Title>
          <BarChart3 size={28} color="#6B4EE6" />
          Insight-Driven Pulse
        </Title>
        <HeaderActions>
            <LastSynced>
            <Clock size={16} />
              Last synced: {pulseData?.generated_at ? new Date(pulseData.generated_at).toLocaleString() : 'N/A'}
          </LastSynced>
          <Button onClick={handleRefresh} disabled={isRefreshing}>
            <RefreshCw size={16} style={{ animation: isRefreshing ? 'spin 1s linear infinite' : 'none' }} />
            {isRefreshing ? 'Refreshing...' : 'Refresh Analysis'}
          </Button>
          <Button variant="secondary" onClick={handleDownload} disabled={isDownloading}>
            <Download size={16} />
            {isDownloading ? 'Downloading...' : 'Download Reviews CSV'}
          </Button>
        </HeaderActions>
      </Header>

      <MainLayout>
        <LeftColumn>
          <Card>
            <WeeklyPulseHeader>
              <WeekInfo>
                <h3 style={{ margin: 0, color: '#1E3A5F', fontSize: '20px' }}>Weekly Product Pulse</h3>
                <WeekBadge>{weeklyPulse.week}</WeekBadge>
              </WeekInfo>
            </WeeklyPulseHeader>

            <ThemesContainer>
              {themes.map(theme => (
                <ThemeCard 
                  key={theme.name}
                  selected={theme.name === selectedTheme}
                  onClick={() => setSelectedTheme(theme.name)}
                >
                  <ThemeHeader>
                    <ThemeName>{theme.name}</ThemeName>
                    <ConfidenceBadge confidence={theme.confidence}>
                      {(theme.confidence * 100).toFixed(0)}%
                    </ConfidenceBadge>
                  </ThemeHeader>
                  <ThemeMeta>
                    <span>{theme.mentions} mentions</span>
                    <span style={{ color: theme.sentiment >= 0 ? '#27AE60' : '#E74C3C' }}>
                      sentiment {theme.sentiment}
                    </span>
                  </ThemeMeta>
                </ThemeCard>
              ))}
            </ThemesContainer>

            <SummaryText>{weeklyPulse.summary}</SummaryText>

            <ActionsSection>
              <ActionsTitle>🔥 3 Actions for Product Team</ActionsTitle>
              <ActionList>
                {(weeklyPulse.actions || []).map((action, idx) => (
                  <ActionItem key={idx}>
                    <ActionNumber>{idx + 1}</ActionNumber>
                    <ActionText>{action}</ActionText>
                  </ActionItem>
                ))}
              </ActionList>
            </ActionsSection>

            <div>
              <h4 style={{ margin: '0 0 12px 0', color: '#1E3A5F', fontSize: '14px' }}>Top Keywords</h4>
              <KeywordsCloud>
                {keywords.map((kw, idx) => (
                  <Keyword key={idx} size={kw.size}>
                    <KeywordLabel>{kw.word}</KeywordLabel>
                    <KeywordCount>{kw.count}</KeywordCount>
                  </Keyword>
                ))}
              </KeywordsCloud>
            </div>
          </Card>

        </LeftColumn>

        <RightColumn>
          <Card>
            <CardHeader>
              <CardTitle><BarChart3 size={20} /> Analytics Dashboard</CardTitle>
            </CardHeader>

            <StatsGrid>
              <StatBox>
                <StatValue>{themes.length}</StatValue>
                <StatLabel>Active Themes</StatLabel>
              </StatBox>
              <StatBox>
                <StatValue>{totalMentions}</StatValue>
                <StatLabel>Total Mentions</StatLabel>
              </StatBox>
              <StatBox>
                <StatValue>{avgConfidence.toFixed(2)}</StatValue>
                <StatLabel>Avg Confidence</StatLabel>
              </StatBox>
              <StatBox>
                <StatValue>{pulseData.word_count}</StatValue>
                <StatLabel>Word Count</StatLabel>
              </StatBox>
            </StatsGrid>

            <div style={{ marginBottom: '20px' }}>
              <h4 style={{ margin: '0 0 12px 0', color: '#1E3A5F', fontSize: '14px' }}>Mention Volume</h4>
              <VolumeChart style={{ height: '140px', marginTop: 0 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={mentionVolumeData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#E8F4FC" />
                    <XAxis dataKey="label" stroke="#5DADE2" fontSize={11} />
                    <YAxis stroke="#5DADE2" fontSize={11} />
                    <Tooltip
                      contentStyle={{ background: 'white', border: '1px solid #E8F4FC', borderRadius: '8px' }}
                    />
                    <Bar dataKey="count" fill="#5DADE2" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </VolumeChart>
            </div>

            <ChartContainer>
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={themeDistributionData}
                    cx="50%"
                    cy="50%"
                    innerRadius={40}
                    outerRadius={70}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {themeDistributionData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={DONUT_COLORS[index % DONUT_COLORS.length]} />
                    ))}
                  </Pie>
                  <Legend verticalAlign="bottom" height={36} iconType="circle" />
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </ChartContainer>
          </Card>

        </RightColumn>
      </MainLayout>

      <QuickTips>
        <QuickTipsTitle>Quick Use Tips</QuickTipsTitle>
        <QuickTip>Click Refresh Analysis to update themes with latest reviews</QuickTip>
        <QuickTip>Click on any theme tag to filter analytics by that theme</QuickTip>
        <QuickTip>Weekly Pulse is limited to 250 words with exactly 3 actionable items</QuickTip>
        <QuickTip>Download Reviews CSV to get raw data for deeper analysis</QuickTip>
      </QuickTips>
    </Container>
  );
};

export default PillarB;
