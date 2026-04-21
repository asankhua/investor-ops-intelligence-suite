import React, { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';
import { Search, Send, ExternalLink, Bot, User, BookOpen } from 'lucide-react';
import { pillarAAPI } from '../services/api';

const Container = styled.div`
  max-width: 1600px;
  margin: 0 auto;
  height: calc(100vh - 40px);
  display: flex;
  flex-direction: column;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 20px;
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

const MainLayout = styled.div`
  display: grid;
  grid-template-columns: 280px 1fr 320px;
  gap: 20px;
  flex: 1;
  min-height: 0;
`;

const Panel = styled.div`
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(30, 58, 95, 0.08);
  display: flex;
  flex-direction: column;
  overflow: hidden;
`;

const PanelHeader = styled.div`
  padding: 16px 20px;
  border-bottom: 1px solid #E8F4FC;
  font-weight: 600;
  color: #1E3A5F;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const PanelContent = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 16px;
`;

const SearchBox = styled.div`
  position: relative;
  margin-bottom: 16px;
`;

const SearchInput = styled.input`
  width: 100%;
  padding: 12px 16px 12px 44px;
  border: 2px solid #E8F4FC;
  border-radius: 8px;
  font-size: 14px;
  color: #1E3A5F;
  
  &:focus {
    outline: none;
    border-color: #5DADE2;
  }
  
  &::placeholder {
    color: #5DADE2;
  }
`;

const SearchIcon = styled(Search)`
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: #5DADE2;
  width: 20px;
  height: 20px;
`;

const FundList = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
`;

const FundItem = styled.div`
  display: flex;
  align-items: center;
  padding: 8px 12px;
  background: #E8F4FC;
  border-radius: 999px;
  text-align: left;
  font-size: 13px;
  font-weight: 500;
  color: #1E3A5F;
  border: 1px solid #D6EAF8;
`;

const ChatContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100%;
`;

const MessagesArea = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const Message = styled.div`
  display: flex;
  gap: 12px;
  align-items: flex-start;
  ${props => props.isUser && 'flex-direction: row-reverse;'}
`;

const Avatar = styled.div`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: ${props => props.isUser ? '#5DADE2' : '#1E3A5F'};
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
`;

const MessageContent = styled.div`
  max-width: 70%;
  background: ${props => props.isUser ? '#5DADE2' : '#F0F7FC'};
  color: ${props => props.isUser ? 'white' : '#1E3A5F'};
  padding: 16px;
  border-radius: 12px;
  border-bottom-left-radius: ${props => props.isUser ? '12px' : '4px'};
  border-bottom-right-radius: ${props => props.isUser ? '4px' : '12px'};
`;

const MessageText = styled.p`
  margin: 0;
  line-height: 1.6;
  font-size: 14px;
`;

const BulletsContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 8px;
`;

const Bullet = styled.div`
  display: flex;
  gap: 8px;
  align-items: flex-start;
`;

const BulletPoint = styled.span`
  color: #5DADE2;
  font-weight: bold;
`;

const BulletText = styled.span`
  flex: 1;
`;

const SourceTag = styled.span`
  background: #5DADE2;
  color: white;
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 4px;
  margin-left: 8px;
  cursor: pointer;
  
  &:hover {
    background: #1E3A5F;
  }
`;

const InputArea = styled.div`
  padding: 16px 20px;
  border-top: 1px solid #E8F4FC;
  display: flex;
  gap: 12px;
`;

const Input = styled.input`
  flex: 1;
  padding: 14px 20px;
  border: 2px solid #E8F4FC;
  border-radius: 8px;
  font-size: 14px;
  color: #1E3A5F;
  
  &:focus {
    outline: none;
    border-color: #5DADE2;
  }
  
  &::placeholder {
    color: #5DADE2;
  }
`;

const SendButton = styled.button`
  width: 48px;
  height: 48px;
  border: none;
  background: #1E3A5F;
  color: white;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  
  &:hover {
    background: #2a4a73;
    transform: translateY(-2px);
  }
  
  &:disabled {
    background: #ccc;
    cursor: not-allowed;
    transform: none;
  }
`;

const SourceItem = styled.div`
  padding: 12px;
  background: #F8FBFD;
  border-radius: 8px;
  margin-bottom: 8px;
  border-left: 3px solid #5DADE2;
`;

const SourceTitle = styled.div`
  font-weight: 600;
  color: #1E3A5F;
  font-size: 13px;
  margin-bottom: 4px;
`;

const SourcePreview = styled.div`
  font-size: 12px;
  color: #5DADE2;
  line-height: 1.5;
`;

const EmptyState = styled.div`
  font-size: 13px;
  color: #5DADE2;
  padding: 8px 4px;
`;

const ViewSourceButton = styled.button`
  display: flex;
  align-items: center;
  gap: 4px;
  background: none;
  border: none;
  color: #5DADE2;
  font-size: 12px;
  cursor: pointer;
  margin-top: 8px;
  text-decoration: none;
  
  &:hover {
    color: #1E3A5F;
  }
`;

const SelfRAGPanel = styled.div`
  background: #E8F4FC;
  border-radius: 8px;
  padding: 16px;
  margin-top: 16px;
`;

const SelfRAGTitle = styled.div`
  font-weight: 600;
  color: #1E3A5F;
  margin-bottom: 12px;
  font-size: 14px;
`;

const SelfRAGGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
`;

const SelfRAGItem = styled.div`
  background: white;
  padding: 12px;
  border-radius: 6px;
  font-size: 12px;
`;

const SelfRAGLabel = styled.div`
  color: #5DADE2;
  font-size: 11px;
  margin-bottom: 4px;
`;

const SelfRAGValue = styled.div`
  color: #1E3A5F;
  font-weight: 500;
`;

const QuickTips = styled.div`
  background: #1E3A5F;
  border-radius: 12px;
  padding: 16px;
  margin-top: 20px;
  color: white;
`;

const QuickTipsTitle = styled.h4`
  margin: 0 0 8px 0;
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

const PillarA = () => {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([
    {
      isUser: false,
      text: 'Hello! I\'m your AI Advisor. Ask me anything about mutual funds, fees, or investment queries.',
      bullets: [],
      sources: []
    }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [funds, setFunds] = useState([]);
  const [sources, setSources] = useState([]);
  const [activeCitations, setActiveCitations] = useState([]);
  const [loadError, setLoadError] = useState('');
  const messagesEndRef = useRef(null);

  const filteredFunds = funds.filter(fund =>
    fund.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    const loadKnowledgeBaseData = async () => {
      try {
        const [fundsResponse, sourcesResponse] = await Promise.all([
          pillarAAPI.searchFunds(''),
          pillarAAPI.getSources()
        ]);

        const fetchedFunds = fundsResponse?.data?.funds || [];
        const fetchedSources = sourcesResponse?.data?.sources || [];

        setFunds(fetchedFunds);
        setSources(fetchedSources);
        setLoadError('');

      } catch (error) {
        console.error('Failed to load knowledge base data:', error);
        const errorMessage =
          error?.response?.data?.detail ||
          error?.message ||
          'Unable to load funds. Please verify Knowledge Base API is running.';
        setLoadError(errorMessage);
      }
    };

    loadKnowledgeBaseData();
  }, []);

  const handleSend = async () => {
    if (!query.trim()) return;

    const userMessage = { isUser: true, text: query, bullets: [], sources: [] };
    setMessages(prev => [...prev, userMessage]);
    setQuery('');
    setIsLoading(true);

    try {
      const response = await pillarAAPI.queryRAG({
        query,
        top_k: 6
      });
      const result = response?.data || {};

      const citations = result.citations || [];
      const aiResponse = {
        isUser: false,
        text: `Based on your query about "${result.query || query}", here are the facts:`,
        bullets: (result.bullets || []).map((bullet) => ({
          text: bullet.text,
          source: (bullet.sources || []).join(', ')
        })),
        sources: citations,
        selfRAG: {
          queryExpansion: result?.self_rag?.query_expansion || 'N/A',
          sufficiency: result?.self_rag?.sufficiency_check || 'N/A',
          retrievedChunks: result?.self_rag?.retrieved_chunks ?? 0
        }
      };
      setMessages(prev => [...prev, aiResponse]);
      if (citations.length > 0) setActiveCitations(citations);    } catch (error) {
      const errorMessage = error?.response?.data?.detail || 'Unable to fetch answer from Knowledge Base.';
      setMessages(prev => [
        ...prev,
        {
          isUser: false,
          text: errorMessage,
          bullets: [],
          sources: []
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Container>
      <Header>
        <Title>
          <BookOpen size={28} color="#1E3A5F" />
          Smart-Sync Knowledge Base
        </Title>
      </Header>

      <MainLayout>
        <Panel>
          <PanelHeader>
            <Search size={18} />
            Fund List
          </PanelHeader>
          <PanelContent>
            <SearchBox>
              <SearchIcon />
              <SearchInput 
                placeholder="Search funds..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </SearchBox>
            <FundList>
              {loadError ? (
                <EmptyState>{loadError}</EmptyState>
              ) : filteredFunds.length === 0 ? (
                <EmptyState>No funds found.</EmptyState>
              ) : (
                filteredFunds.map((fund, idx) => (
                  <FundItem
                    key={fund.name || idx}
                  >
                    {fund.name || fund.fund_name || String(fund)}
                  </FundItem>
                ))
              )}
            </FundList>
          </PanelContent>
        </Panel>

        <Panel>
          <PanelHeader>
            <Bot size={18} />
            Conversational Chat
          </PanelHeader>
          <ChatContainer>
            <MessagesArea>
              {messages.map((message, index) => (
                <Message key={index} isUser={message.isUser}>
                  <Avatar isUser={message.isUser}>
                    {message.isUser ? <User size={20} /> : <Bot size={20} />}
                  </Avatar>
                  <MessageContent isUser={message.isUser}>
                    <MessageText>{message.text}</MessageText>
                    {message.bullets && message.bullets.length > 0 && (
                      <BulletsContainer>
                        {message.bullets.map((bullet, idx) => (
                          <Bullet key={idx}>
                            <BulletPoint>•</BulletPoint>
                            <BulletText>
                              {bullet.text}
                              <SourceTag>{bullet.source}</SourceTag>
                            </BulletText>
                          </Bullet>
                        ))}
                      </BulletsContainer>
                    )}
                    {message.selfRAG && (
                      <SelfRAGPanel>
                        <SelfRAGTitle>🔍 Self-RAG Debug Panel</SelfRAGTitle>
                        <SelfRAGGrid>
                          <SelfRAGItem>
                            <SelfRAGLabel>Query Expansion</SelfRAGLabel>
                            <SelfRAGValue>{message.selfRAG.queryExpansion}</SelfRAGValue>
                          </SelfRAGItem>
                          <SelfRAGItem>
                            <SelfRAGLabel>Sufficiency Check</SelfRAGLabel>
                            <SelfRAGValue>{message.selfRAG.sufficiency}</SelfRAGValue>
                          </SelfRAGItem>
                          <SelfRAGItem>
                            <SelfRAGLabel>Retrieved Chunks</SelfRAGLabel>
                            <SelfRAGValue>{message.selfRAG.retrievedChunks}</SelfRAGValue>
                          </SelfRAGItem>
                        </SelfRAGGrid>
                      </SelfRAGPanel>
                    )}
                  </MessageContent>
                </Message>
              ))}
              {isLoading && (
                <Message>
                  <Avatar><Bot size={20} /></Avatar>
                  <MessageContent>
                    <MessageText>Thinking...</MessageText>
                  </MessageContent>
                </Message>
              )}
              <div ref={messagesEndRef} />
            </MessagesArea>
            <InputArea>
              <Input
                placeholder="Type your question..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSend()}
              />
              <SendButton onClick={handleSend} disabled={isLoading || !query.trim()}>
                <Send size={20} />
              </SendButton>
            </InputArea>
          </ChatContainer>
        </Panel>

        <Panel>
          <PanelHeader>
            <BookOpen size={18} />
            Sources & Citations
          </PanelHeader>
          <PanelContent>
            {activeCitations.length === 0 ? (
              <EmptyState>Ask a question to see sources from the Knowledge Base.</EmptyState>
            ) : (
              activeCitations.map((source, idx) => {
                const sourceUrl = source.source_url ||
                  `https://www.google.com/search?q=${encodeURIComponent(source.document || source.name || '')}`;
                return (
                  <SourceItem key={source.chunk_id || idx}>
                    <SourceTitle>[{source.chunk_id || `S${idx + 1}`}] {source.document || source.name || source}</SourceTitle>
                    <SourcePreview>{source.preview || source.description || 'Source available from Knowledge Base.'}</SourcePreview>
                    <ViewSourceButton as="a" href={sourceUrl} target="_blank" rel="noopener noreferrer">
                      View Source <ExternalLink size={12} />
                    </ViewSourceButton>
                  </SourceItem>
                );
              })
            )}
          </PanelContent>
        </Panel>
      </MainLayout>

      <QuickTips>
        <QuickTipsTitle>Quick Use Tips</QuickTipsTitle>
        <QuickTip>Type a fund name in the search box to filter the fund list</QuickTip>
        <QuickTip>Fund list is reference-only and shown as compact pills</QuickTip>
        <QuickTip>Responses include 6 bullet points max with source citations [M1], [M1.1]</QuickTip>
        <QuickTip>Self-RAG debug panel shows query expansion and sufficiency checks</QuickTip>
      </QuickTips>
    </Container>
  );
};

export default PillarA;
