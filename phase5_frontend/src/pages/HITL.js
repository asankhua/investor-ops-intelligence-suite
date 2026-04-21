import React, { useState } from 'react';
import { useQuery } from 'react-query';
import styled from 'styled-components';
import { Settings, CheckCircle, XCircle, Clock, Calendar, Mail, FileText, Edit3, Send, AlertTriangle } from 'lucide-react';
import { hitlAPI } from '../services/api';

const Container = styled.div`
  max-width: 1400px;
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

const Badge = styled.span`
  background: ${props => props.variant === 'pending' ? '#FDF2E9' : '#E8FCF0'};
  color: ${props => props.variant === 'pending' ? '#E67E22' : '#27AE60'};
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
`;

const MainLayout = styled.div`
  display: grid;
  grid-template-columns: 1fr 420px;
  gap: 24px;
`;

const LeftColumn = styled.div`
  display: flex;
  flex-direction: column;
  gap: 20px;
`;

const RightColumn = styled.div``;

const Card = styled.div`
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(30, 58, 95, 0.08);
  overflow: hidden;
`;

const CardHeader = styled.div`
  padding: 20px 24px;
  border-bottom: 1px solid #E8F4FC;
  display: flex;
  justify-content: space-between;
  align-items: center;
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

const Table = styled.table`
  width: 100%;
  border-collapse: collapse;
`;

const Th = styled.th`
  text-align: left;
  padding: 16px 24px;
  font-size: 13px;
  font-weight: 600;
  color: #5DADE2;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  background: #F8FBFD;
  border-bottom: 1px solid #E8F4FC;
`;

const Td = styled.td`
  padding: 16px 24px;
  border-bottom: 1px solid #E8F4FC;
  color: #1E3A5F;
  font-size: 14px;
`;

const Tr = styled.tr`
  cursor: pointer;
  transition: background 0.2s;
  background: ${props => props.selected ? '#E8F4FC' : 'transparent'};
  
  &:hover {
    background: #F8FBFD;
  }
`;

const StatusBadge = styled.span`
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  background: ${props => props.status === 'pending' ? '#FDF2E9' : props.status === 'approved' ? '#E8FCF0' : '#FCE8E8'};
  color: ${props => props.status === 'pending' ? '#E67E22' : props.status === 'approved' ? '#27AE60' : '#E74C3C'};
`;

const ActionButtons = styled.div`
  display: flex;
  gap: 8px;
`;

const IconButton = styled.button`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  background: ${props => props.variant === 'approve' ? '#E8FCF0' : props.variant === 'reject' ? '#FCE8E8' : '#F8FBFD'};
  color: ${props => props.variant === 'approve' ? '#27AE60' : props.variant === 'reject' ? '#E74C3C' : '#5DADE2'};
  
  &:hover {
    transform: scale(1.1);
  }
`;

const EmailPreviewCard = styled.div`
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(30, 58, 95, 0.08);
  padding: 24px;
  height: fit-content;
`;

const EmailHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 2px solid #E8F4FC;
`;

const EmailIcon = styled.div`
  width: 48px;
  height: 48px;
  background: #E8F4FC;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #1E3A5F;
`;

const EmailTitle = styled.h3`
  color: #1E3A5F;
  font-size: 16px;
  font-weight: 600;
  margin: 0;
`;

const EmailSubtitle = styled.p`
  color: #5DADE2;
  font-size: 13px;
  margin: 4px 0 0 0;
`;

const EmailField = styled.div`
  margin-bottom: 16px;
`;

const EmailLabel = styled.label`
  display: block;
  font-size: 12px;
  color: #5DADE2;
  font-weight: 600;
  margin-bottom: 6px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

const EmailInput = styled.input`
  width: 100%;
  padding: 10px 14px;
  border: 1px solid #E8F4FC;
  border-radius: 6px;
  font-size: 14px;
  color: #1E3A5F;
  background: #F8FBFD;
  
  &:focus {
    outline: none;
    border-color: #5DADE2;
  }
`;

const EmailTextArea = styled.textarea`
  width: 100%;
  min-height: 200px;
  padding: 14px;
  border: 1px solid #E8F4FC;
  border-radius: 6px;
  font-size: 14px;
  line-height: 1.6;
  color: #1E3A5F;
  background: #F8FBFD;
  resize: vertical;
  font-family: inherit;
  
  &:focus {
    outline: none;
    border-color: #5DADE2;
  }
`;

const ContextBanner = styled.div`
  background: #FDF2E9;
  border-left: 4px solid #E67E22;
  padding: 12px 16px;
  margin-bottom: 16px;
  border-radius: 6px;
`;

const ContextText = styled.p`
  color: #1E3A5F;
  font-size: 13px;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const PreviewActions = styled.div`
  display: flex;
  gap: 12px;
  margin-top: 20px;
`;

const PreviewButton = styled.button`
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px;
  border: 2px solid ${props => props.variant === 'primary' ? '#1E3A5F' : '#E8F4FC'};
  border-radius: 8px;
  background: ${props => props.variant === 'primary' ? '#1E3A5F' : 'white'};
  color: ${props => props.variant === 'primary' ? 'white' : '#1E3A5F'};
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  
  &:hover {
    background: ${props => props.variant === 'primary' ? '#2a4a73' : '#F8FBFD'};
  }
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
`;

const StatCard = styled.div`
  background: white;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(30, 58, 95, 0.08);
  text-align: center;
`;

const StatValue = styled.div`
  font-size: 32px;
  font-weight: 700;
  color: #1E3A5F;
  margin-bottom: 4px;
`;

const StatLabel = styled.div`
  font-size: 13px;
  color: #5DADE2;
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
  margin: 4px 0;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.9);
  &::before {
    content: '💡 ';
  }
`;

const BookingCode = styled.span`
  font-family: monospace;
  background: #E8F4FC;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 13px;
`;

const EmptyState = styled.div`
  padding: 24px;
  text-align: center;
  color: #5DADE2;
  font-size: 14px;
`;

const HITL = () => {
  const [selectedAction, setSelectedAction] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const [emailDraft, setEmailDraft] = useState({
    to: '',
    subject: '',
    body: ''
  });

  const { data: actionsPayload, isLoading, isError, error, refetch: refetchActions } = useQuery(
    'hitlActions',
    async () => {
      const res = await hitlAPI.getActions();
      return res?.data || {};
    }
  );

  const allActions = actionsPayload?.actions || [];
  const onlyPending = [...allActions]
    .filter((a) => a.status === 'pending')
    .sort((a, b) => new Date(b.requested_at || 0).getTime() - new Date(a.requested_at || 0).getTime());
  const resolvedActions = allActions.filter((a) => a.status === 'approved' || a.status === 'rejected');
  const selected = onlyPending.find((a) => a.id === selectedAction) || onlyPending[0];
  const selectedBookingCode = selected?.booking_code;

  const avgResponseMinutes = onlyPending.length
    ? Math.round(
        onlyPending
          .map((a) => (a.requested_at ? (Date.now() - new Date(a.requested_at).getTime()) / 60000 : 0))
          .reduce((sum, v) => sum + v, 0) / onlyPending.length
      )
    : 0;

  useQuery(
    ['hitlEmailPreview', selectedBookingCode],
    async () => {
      if (!selectedBookingCode) return null;
      const res = await hitlAPI.getEmailPreview(selectedBookingCode);
      const draft = res?.data || {};
      setEmailDraft({
        to: draft.status === 'not_found' ? '' : (draft.to || ''),
        subject: draft.status === 'not_found' ? '' : (draft.subject || ''),
        body: draft.status === 'not_found' ? '' : (draft.body || '')
      });
      return draft;
    },
    { enabled: Boolean(selectedBookingCode) }
  );

  const handleApprove = async (id) => {
    await hitlAPI.approveAction(id);
    await refetchActions();
  };

  const handleReject = async (id) => {
    await hitlAPI.rejectAction(id, { reason: 'Rejected from HITL UI' });
    await refetchActions();
  };

  const handleSendEmail = async () => {
    if (!selectedBookingCode) return;
    await hitlAPI.sendEmail(selectedBookingCode, { approved: true });
    await refetchActions();
  };

  const handleEditEmail = async () => {
    if (isEditing && selectedBookingCode) {
      await hitlAPI.editEmail(selectedBookingCode, {
        subject: emailDraft.subject,
        body: emailDraft.body
      });
    }
    setIsEditing(!isEditing);
  };

  if (isLoading) {
    return (
      <Container>
        <EmptyState>Loading HITL actions...</EmptyState>
      </Container>
    );
  }

  if (isError) {
    return (
      <Container>
        <EmptyState>{error?.response?.data?.detail || 'Failed to load HITL data.'}</EmptyState>
      </Container>
    );
  }

  return (
    <Container>
      <Header>
        <Title>
          <Settings size={28} color="#1E3A5F" />
          Human-in-the-Loop Approval Center
        </Title>
        <Badge variant="pending">{onlyPending.length} Pending</Badge>
      </Header>

      <StatsGrid>
        <StatCard>
          <StatValue>{onlyPending.length}</StatValue>
          <StatLabel>Pending Approvals</StatLabel>
        </StatCard>
        <StatCard>
          <StatValue>{resolvedActions.length}</StatValue>
          <StatLabel>Resolved Actions</StatLabel>
        </StatCard>
        <StatCard>
          <StatValue>{avgResponseMinutes}m</StatValue>
          <StatLabel>Avg Response Time</StatLabel>
        </StatCard>
      </StatsGrid>

      <MainLayout>
        <LeftColumn>
          <Card>
            <CardHeader>
              <CardTitle>
                <Clock size={20} />
                Pending Actions ({onlyPending.length})
              </CardTitle>
            </CardHeader>
            <Table>
              <thead>
                <tr>
                  <Th>Action</Th>
                  <Th>Booking Code</Th>
                  <Th>Details</Th>
                  <Th>Requested</Th>
                  <Th>Status</Th>
                  <Th>Actions</Th>
                </tr>
              </thead>
              <tbody>
                {onlyPending.length === 0 && (
                  <tr>
                    <Td colSpan={6} style={{ textAlign: 'center', color: '#5DADE2' }}>
                      No pending HITL actions.
                    </Td>
                  </tr>
                )}
                {onlyPending.map(action => (
                  <Tr 
                    key={action.id} 
                    selected={selectedAction === action.id}
                    onClick={() => setSelectedAction(action.id)}
                  >
                    <Td>
                      {action.type === 'calendar' ? (
                        <><Calendar size={16} style={{ marginRight: 8 }} />Calendar Hold</>
                      ) : (
                        <><Mail size={16} style={{ marginRight: 8 }} />Email Draft</>
                      )}
                    </Td>
                    <Td><BookingCode>{action.booking_code}</BookingCode></Td>
                    <Td>{action.type === 'calendar' ? action.details?.datetime : action.details?.subject}</Td>
                    <Td>{action.requested_at ? new Date(action.requested_at).toLocaleString() : '-'}</Td>
                    <Td>
                      <StatusBadge status={action.status}>
                        <Clock size={12} />
                        {action.status}
                      </StatusBadge>
                    </Td>
                    <Td>
                      <ActionButtons>
                        <IconButton variant="approve" onClick={(e) => { e.stopPropagation(); handleApprove(action.id); }}>
                          <CheckCircle size={18} />
                        </IconButton>
                        <IconButton variant="reject" onClick={(e) => { e.stopPropagation(); handleReject(action.id); }}>
                          <XCircle size={18} />
                        </IconButton>
                      </ActionButtons>
                    </Td>
                  </Tr>
                ))}
              </tbody>
            </Table>
          </Card>
        </LeftColumn>

        <RightColumn>
          <EmailPreviewCard>
            <EmailHeader>
              <EmailIcon>
                <Mail size={24} />
              </EmailIcon>
              <div>
                <EmailTitle>Preview Draft Email</EmailTitle>
                <EmailSubtitle>Booking: <BookingCode>{selectedBookingCode || '-'}</BookingCode></EmailSubtitle>
              </div>
            </EmailHeader>

            <ContextBanner>
              <ContextText>
                <AlertTriangle size={16} color="#E67E22" />
                Includes Weekly Pulse market context
              </ContextText>
            </ContextBanner>

            <EmailField>
              <EmailLabel>To</EmailLabel>
              <EmailInput 
                value={emailDraft.to} 
                onChange={(e) => setEmailDraft({...emailDraft, to: e.target.value})}
                readOnly={!isEditing}
              />
            </EmailField>

            <EmailField>
              <EmailLabel>Subject</EmailLabel>
              <EmailInput 
                value={emailDraft.subject} 
                onChange={(e) => setEmailDraft({...emailDraft, subject: e.target.value})}
                readOnly={!isEditing}
              />
            </EmailField>

            <EmailField>
              <EmailLabel>Body</EmailLabel>
              <EmailTextArea 
                value={emailDraft.body} 
                onChange={(e) => setEmailDraft({...emailDraft, body: e.target.value})}
                readOnly={!isEditing}
              />
            </EmailField>

            <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: '13px', color: '#5DADE2', marginTop: '12px' }}>
              <FileText size={14} />
              Synced through Phase 4 shared state
            </div>

            <PreviewActions>
              <PreviewButton variant="primary" onClick={handleSendEmail} disabled={!selectedBookingCode}>
                <Send size={16} />
                Send
              </PreviewButton>
              <PreviewButton onClick={handleEditEmail} disabled={!selectedBookingCode}>
                <Edit3 size={16} />
                {isEditing ? 'Done' : 'Edit'}
              </PreviewButton>
            </PreviewActions>
          </EmailPreviewCard>
        </RightColumn>
      </MainLayout>

      <QuickTips>
        <QuickTipsTitle>Quick Use Tips</QuickTipsTitle>
        <QuickTip>Review pending actions in the left panel and approve/reject with one click</QuickTip>
        <QuickTip>Preview and edit email drafts on the right before sending</QuickTip>
        <QuickTip>Email drafts automatically include Weekly Pulse market context</QuickTip>
        <QuickTip>All booking details are synced to the tracking Google Doc automatically</QuickTip>
      </QuickTips>
    </Container>
  );
};

export default HITL;
