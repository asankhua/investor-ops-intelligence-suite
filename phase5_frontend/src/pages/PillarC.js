import React, { useState, useEffect, useRef } from 'react';
import { useQuery } from 'react-query';
import styled from 'styled-components';
import { Mic, Play, Square, X, Bot, User, Volume2, CheckCircle, Calendar, Mail, FileText, Clock, Wrench, Settings, XCircle, Edit3, Send, AlertTriangle } from 'lucide-react';
import { pillarCAPI, hitlAPI, pillarBAPI } from '../services/api';

const Container = styled.div`
  max-width: 1600px;
  margin: 0 auto;
  min-height: calc(100vh - 40px);
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
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
  margin: 0;
`;

const PipelineStatus = styled.div`
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: #1E3A5F;
  color: white;
  padding: 10px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  margin-left: auto;
`;

const PipelineSteps = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: 16px;
`;

const Step = styled.div`
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
  background: ${props => props.active ? '#5DADE2' : 'transparent'};
  opacity: ${props => props.completed ? 1 : 0.6};
`;

const MainLayout = styled.div`
  display: grid;
  grid-template-columns: 320px 1fr 360px;
  gap: 20px;
  margin-bottom: 20px;
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
  font-size: 15px;
`;

const PanelContent = styled.div`
  flex: 1;
  padding: 20px;
  display: flex;
  flex-direction: column;
`;

const RecordingArea = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24px;
  padding: 40px 20px;
  background: #F8FBFD;
  border-radius: 12px;
  margin-bottom: 20px;
`;

const RecordButton = styled.button`
  width: 100px;
  height: 100px;
  border-radius: 50%;
  border: none;
  background: ${props => props.recording ? '#E74C3C' : '#E74C3C'};
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  box-shadow: 0 4px 20px ${props => props.recording ? 'rgba(231, 76, 60, 0.4)' : 'rgba(231, 76, 60, 0.3)'};
  animation: ${props => props.recording ? 'pulse 1.5s ease-in-out infinite' : 'none'};
  
  &:hover {
    transform: scale(1.05);
  }
  
  @keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.05); }
  }
`;

const RecordingControls = styled.div`
  display: flex;
  gap: 12px;
`;

const ControlButton = styled.button`
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  background: ${props => props.variant === 'cancel' ? '#FCE8E8' : props.variant === 'play' ? '#E8FCF0' : '#E8F4FC'};
  color: ${props => props.variant === 'cancel' ? '#E74C3C' : props.variant === 'play' ? '#27AE60' : '#1E3A5F'};
  
  &:hover {
    opacity: 0.8;
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const Waveform = styled.div`
  height: 60px;
  background: linear-gradient(90deg, #E8F4FC 0%, #5DADE2 50%, #E8F4FC 100%);
  border-radius: 8px;
  width: 100%;
  margin-bottom: 20px;
  display: ${props => props.visible ? 'flex' : 'none'};
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  
  &::after {
    content: '';
    position: absolute;
    left: 0;
    right: 0;
    height: 2px;
    background: #5DADE2;
    animation: wave 1s ease-in-out infinite;
  }
  
  @keyframes wave {
    0%, 100% { transform: scaleY(1); }
    50% { transform: scaleY(1.5); }
  }
`;

const AgentVoiceSection = styled.div`
  background: #E8F4FC;
  border-radius: 8px;
  padding: 16px;
  margin-top: auto;
`;

const AgentVoiceHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  color: #1E3A5F;
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 12px;
`;

const AgentVoicePlayer = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  background: white;
  padding: 12px;
  border-radius: 8px;
`;

const PlayButton = styled.button`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: none;
  background: #1E3A5F;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &:hover {
    background: #2a4a73;
  }
`;

const ChatContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100%;
`;

const MessagesArea = styled.div`
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 16px 0;
  scroll-behavior: smooth;
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
  max-width: 80%;
  background: ${props => props.isUser ? '#5DADE2' : '#F0F7FC'};
  color: ${props => props.isUser ? 'white' : '#1E3A5F'};
  padding: 14px 18px;
  border-radius: 12px;
  border-bottom-left-radius: ${props => props.isUser ? '12px' : '4px'};
  border-bottom-right-radius: ${props => props.isUser ? '4px' : '12px'};
  font-size: 14px;
  line-height: 1.5;
  white-space: pre-wrap;
`;

const InputToggle = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #F8FBFD;
  border-radius: 8px;
  margin-bottom: 12px;
`;

const ToggleLabel = styled.span`
  font-size: 13px;
  color: #5DADE2;
`;

const Toggle = styled.div`
  display: flex;
  background: #E8F4FC;
  border-radius: 20px;
  padding: 4px;
  gap: 4px;
`;

const ToggleOption = styled.button`
  padding: 6px 16px;
  border-radius: 16px;
  border: none;
  font-size: 13px;
  cursor: pointer;
  background: ${props => props.active ? '#1E3A5F' : 'transparent'};
  color: ${props => props.active ? 'white' : '#5DADE2'};
`;

const InputArea = styled.div`
  display: flex;
  gap: 12px;
  padding-top: 12px;
  border-top: 1px solid #E8F4FC;
`;

const Input = styled.input`
  flex: 1;
  padding: 12px 16px;
  border: 2px solid #E8F4FC;
  border-radius: 8px;
  font-size: 14px;
  color: #1E3A5F;
  
  &:focus {
    outline: none;
    border-color: #5DADE2;
  }
`;

const SendButton = styled.button`
  padding: 12px 20px;
  border: none;
  border-radius: 8px;
  background: #1E3A5F;
  color: white;
  font-weight: 500;
  cursor: pointer;
  
  &:hover {
    background: #2a4a73;
  }
`;

const BookingCard = styled.div`
  background: ${props => props.status === 'confirmed' ? '#E8FCF0' : '#F8FBFD'};
  border: 2px solid ${props => props.status === 'confirmed' ? '#27AE60' : '#E8F4FC'};
  border-radius: 12px;
  padding: 20px;
`;

const BookingHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  color: ${props => props.status === 'confirmed' ? '#27AE60' : '#1E3A5F'};
  font-weight: 600;
  font-size: 16px;
  margin-bottom: 16px;
`;

const BookingDetail = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid ${props => props.status === 'confirmed' ? 'rgba(39, 174, 96, 0.2)' : '#E8F4FC'};
  
  &:last-child {
    border-bottom: none;
  }
`;

const DetailIcon = styled.div`
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: ${props => props.status === 'confirmed' ? '#E8FCF0' : '#E8F4FC'};
  display: flex;
  align-items: center;
  justify-content: center;
  color: ${props => props.status === 'confirmed' ? '#27AE60' : '#5DADE2'};
`;

const DetailContent = styled.div`
  flex: 1;
`;

const DetailLabel = styled.div`
  font-size: 12px;
  color: #5DADE2;
  margin-bottom: 2px;
`;

const DetailValue = styled.div`
  font-size: 14px;
  color: #1E3A5F;
  font-weight: 500;
`;

const ActionButtons = styled.div`
  display: flex;
  gap: 12px;
  margin-top: 20px;
`;

const ActionButton = styled.button`
  flex: 1;
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

const QuickTips = styled.div`
  background: #1E3A5F;
  border-radius: 12px;
  padding: 20px;
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

const ThemeContextBadge = styled.div`
  margin: 10px 0 0 0;
  padding: 8px 12px;
  border-radius: 8px;
  background: #E8F4FC;
  color: #1E3A5F;
  font-size: 12px;
  font-weight: 500;
`;

const ThemesBar = styled.div`
  display: flex;
  align-items: center;
  gap: 10px;
  background: white;
  border-radius: 10px;
  padding: 12px 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(30, 58, 95, 0.08);
  flex-wrap: wrap;
`;

const ThemesLabel = styled.div`
  font-size: 12px;
  font-weight: 700;
  color: #5DADE2;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  white-space: nowrap;
`;

const ThemeChip = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  background: #E8F4FC;
  border-radius: 20px;
  padding: 6px 14px;
  font-size: 13px;
  font-weight: 600;
  color: #1E3A5F;
`;

const ThemeConfidence = styled.span`
  background: #1E3A5F;
  color: white;
  border-radius: 10px;
  padding: 2px 7px;
  font-size: 11px;
  font-weight: 600;
`;

// ── HITL merged styles ──────────────────────────────────────────────────────

const HITLSection = styled.div`
  margin-top: 24px;
`;

const TabBar = styled.div`
  display: flex;
  gap: 4px;
  background: white;
  border-radius: 12px 12px 0 0;
  padding: 8px 8px 0;
  box-shadow: 0 2px 8px rgba(30, 58, 95, 0.08);
  border-bottom: 2px solid #E8F4FC;
`;

const Tab = styled.button`
  padding: 10px 20px;
  border: none;
  border-radius: 8px 8px 0 0;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  background: ${props => props.active ? '#1E3A5F' : 'transparent'};
  color: ${props => props.active ? 'white' : '#5DADE2'};
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 8px;
  &:hover { background: ${props => props.active ? '#1E3A5F' : '#E8F4FC'}; }
`;

const HITLBody = styled.div`
  background: white;
  border-radius: 0 0 12px 12px;
  box-shadow: 0 2px 8px rgba(30, 58, 95, 0.08);
  padding: 24px;
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
`;

const StatCard = styled.div`
  background: #F8FBFD;
  border-radius: 10px;
  padding: 20px;
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

const HITLLayout = styled.div`
  display: grid;
  grid-template-columns: 1fr 560px;
  gap: 24px;
`;

const Table = styled.table`
  width: 100%;
  border-collapse: collapse;
`;

const Th = styled.th`
  text-align: left;
  padding: 12px 16px;
  font-size: 12px;
  font-weight: 600;
  color: #5DADE2;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  background: #F8FBFD;
  border-bottom: 1px solid #E8F4FC;
`;

const Td = styled.td`
  padding: 14px 16px;
  border-bottom: 1px solid #E8F4FC;
  color: #1E3A5F;
  font-size: 14px;
`;

const Tr = styled.tr`
  cursor: pointer;
  background: ${props => props.selected ? '#E8F4FC' : 'transparent'};
  &:hover { background: #F8FBFD; }
`;

const StatusBadge = styled.span`
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  background: ${props => props.status === 'pending' ? '#FDF2E9' : props.status === 'approved' ? '#E8FCF0' : '#FCE8E8'};
  color: ${props => props.status === 'pending' ? '#E67E22' : props.status === 'approved' ? '#27AE60' : '#E74C3C'};
`;

const IconButton = styled.button`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  background: ${props => props.variant === 'approve' ? '#E8FCF0' : props.variant === 'reject' ? '#FCE8E8' : '#F8FBFD'};
  color: ${props => props.variant === 'approve' ? '#27AE60' : props.variant === 'reject' ? '#E74C3C' : '#5DADE2'};
  &:hover { transform: scale(1.1); }
`;

const EmailPreviewCard = styled.div`
  background: #F8FBFD;
  border-radius: 10px;
  padding: 20px;
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
  background: white;
  margin-bottom: 14px;
  box-sizing: border-box;
  &:focus { outline: none; border-color: #5DADE2; }
`;

const EmailTextArea = styled.textarea`
  width: 100%;
  min-height: 320px;
  padding: 12px;
  border: 1px solid #E8F4FC;
  border-radius: 6px;
  font-size: 14px;
  line-height: 1.6;
  color: #1E3A5F;
  background: white;
  resize: vertical;
  font-family: inherit;
  box-sizing: border-box;
  &:focus { outline: none; border-color: #5DADE2; }
`;

const ContextBanner = styled.div`
  background: #FDF2E9;
  border-left: 4px solid #E67E22;
  padding: 10px 14px;
  margin-bottom: 14px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #1E3A5F;
`;

const PreviewActions = styled.div`
  display: flex;
  gap: 12px;
  margin-top: 16px;
`;

const PreviewButton = styled.button`
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px;
  border: 2px solid ${props => props.variant === 'primary' ? '#1E3A5F' : '#E8F4FC'};
  border-radius: 8px;
  background: ${props => props.variant === 'primary' ? '#1E3A5F' : 'white'};
  color: ${props => props.variant === 'primary' ? 'white' : '#1E3A5F'};
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  &:hover { background: ${props => props.variant === 'primary' ? '#2a4a73' : '#F8FBFD'}; }
  &:disabled { opacity: 0.5; cursor: not-allowed; }
`;

const BookingCode = styled.span`
  font-family: monospace;
  background: #E8F4FC;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 13px;
`;

const PillarC = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingDuration, setRecordingDuration] = useState(0);
  const [inputMode, setInputMode] = useState('text');
  const [inputText, setInputText] = useState('');
  const [messages, setMessages] = useState([
    { isUser: false, text: 'Hello! I am your RM scheduling assistant. I use Weekly Product Pulse themes to help schedule a call.' }
  ]);
  const [bookingStatus, setBookingStatus] = useState('pending');
  const [pipelineStep, setPipelineStep] = useState('idle');
  const [pipelineStatuses, setPipelineStatuses] = useState({});
  const [recordingId, setRecordingId] = useState(null);
  const [lastRecordingAudioId, setLastRecordingAudioId] = useState(null);
  const [recordedAudioUrl, setRecordedAudioUrl] = useState(null);
  const [recordedAudioBlob, setRecordedAudioBlob] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isSendingVoice, setIsSendingVoice] = useState(false);
  const mediaRecorderRef = useRef(null);
  const mediaStreamRef = useRef(null);
  const audioChunksRef = useRef([]);
  const messagesEndRef = useRef(null);
  const [themeContext, setThemeContext] = useState({ topTheme: null, confidence: null });
  const [booking, setBooking] = useState({
    code: '-',
    date: '-',
    time: '-',
    rm: 'Advisor',
    status: 'Awaiting request'
  });

  // fetch Weekly Pulse themes on mount
  const [pulseThemes, setPulseThemes] = useState([]);
  const [themesFetching, setThemesFetching] = useState(false);

  const handleRefreshThemes = async () => {
    setThemesFetching(true);
    setPulseThemes([]);
    try {
      const [themesRes, greetRes] = await Promise.all([
        pillarBAPI.getThemes(),
        pillarCAPI.sendMessage('hello'),
      ]);
      setPulseThemes(themesRes?.data?.themes || []);
      const responseText = greetRes?.data?.response_text;
      const ctx = greetRes?.data?.theme_context;
      if (responseText) setMessages([{ isUser: false, text: responseText }]);
      if (ctx) setThemeContext({ topTheme: ctx.top_theme || null, confidence: ctx.confidence ?? null });
    } finally {
      setThemesFetching(false);
    }
  };

  // ── HITL state ──────────────────────────────────────────────────────────────
  const [hitlTab, setHitlTab] = useState('pending');
  const [selectedAction, setSelectedAction] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const [emailDraft, setEmailDraft] = useState({ to: '', subject: '', body: '' });

  const { data: actionsPayload, refetch: refetchActions } = useQuery(
    'hitlActions',
    async () => { const res = await hitlAPI.getActions(); return res?.data || {}; },
    { refetchInterval: 5000 }
  );
  const allActions = actionsPayload?.actions || [];
  // Deduplicate: one row per booking_code (prefer email action, merge status)
  const dedupedActions = Object.values(
    allActions.reduce((acc, a) => {
      const key = a.booking_code;
      if (!acc[key] || a.type === 'email') acc[key] = a;
      return acc;
    }, {})
  );
  const onlyPending = dedupedActions.filter(a => a.status === 'pending')
    .sort((a, b) => new Date(b.requested_at || 0) - new Date(a.requested_at || 0));
  const resolvedActions = dedupedActions.filter(a => a.status === 'approved' || a.status === 'rejected');
  const selectedHITL = onlyPending.find(a => a.id === selectedAction) || onlyPending[0];
  const selectedBookingCode = selectedHITL?.booking_code;
  const avgResponseMinutes = onlyPending.length
    ? Math.round(onlyPending.map(a => a.requested_at ? (Date.now() - new Date(a.requested_at).getTime()) / 60000 : 0)
        .reduce((s, v) => s + v, 0) / onlyPending.length) : 0;

  useQuery(
    ['hitlEmailPreview', selectedBookingCode],
    async () => {
      if (!selectedBookingCode) return null;
      const res = await hitlAPI.getEmailPreview(selectedBookingCode);
      const draft = res?.data || {};
      setEmailDraft({
        to: draft.status === 'not_found' ? '' : (draft.to || ''),
        subject: draft.status === 'not_found' ? '' : (draft.subject || ''),
        body: draft.status === 'not_found' ? '' : (draft.body || ''),
      });
      return draft;
    },
    { enabled: Boolean(selectedBookingCode) }
  );

  const handleHITLApprove = async (id) => { await hitlAPI.approveAction(id); await refetchActions(); };
  const handleHITLReject = async (id) => { await hitlAPI.rejectAction(id, { reason: 'Rejected from UI' }); await refetchActions(); };
  const [sendingEmail, setSendingEmail] = useState(false);
  const handleSendEmail = async () => {
    if (!selectedBookingCode) return;
    setSendingEmail(true);
    try {
      await hitlAPI.sendEmail(selectedBookingCode, { approved: true });
      await refetchActions();
    } finally {
      setSendingEmail(false);
    }
  };
  const handleEditEmail = async () => {
    if (isEditing && selectedBookingCode) {
      await hitlAPI.editEmail(selectedBookingCode, { subject: emailDraft.subject, body: emailDraft.body });
    }
    setIsEditing(!isEditing);
  };

  useEffect(() => {
    let interval;
    if (isRecording) {
      interval = setInterval(() => {
        setRecordingDuration(prev => prev + 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isRecording]);

  useEffect(() => {
    return () => {
      if (recordedAudioUrl) {
        URL.revokeObjectURL(recordedAudioUrl);
      }
      if (mediaStreamRef.current) {
        mediaStreamRef.current.getTracks().forEach((track) => track.stop());
      }
    };
  }, [recordedAudioUrl]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
  }, [messages]);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const refreshPipeline = async () => {
    try {
      const statusRes = await pillarCAPI.getPipelineStatus();
      const steps = statusRes?.data?.steps || [];
      const statusMap = {};
      steps.forEach((step) => {
        statusMap[step.id] = step.status;
      });
      setPipelineStatuses(statusMap);
      const active = steps.find((s) => s.status === 'active');
      const activeStep = active?.id || 'idle';
      setPipelineStep(activeStep);
    } catch (_) {
      setPipelineStatuses({});
      setPipelineStep('idle');
    }
  };

  useEffect(() => {
    refreshPipeline();
    const t = setInterval(refreshPipeline, 3000);
    return () => clearInterval(t);
  }, []);

  useEffect(() => {
    // Auto-load themes and greeting on mount
    handleRefreshThemes();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleRecord = async () => {
    if (isRecording && recordingId) {
      setIsRecording(false);
      try {
        if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
          mediaRecorderRef.current.stop();
        }
        if (mediaStreamRef.current) {
          mediaStreamRef.current.getTracks().forEach((track) => track.stop());
          mediaStreamRef.current = null;
        }
        const stopRes = await pillarCAPI.stopRecording(recordingId);
        const duration = stopRes?.data?.duration;
        const audioUrl = stopRes?.data?.audio_url || '';
        const maybeAudioId = audioUrl.split('/').pop();
        if (maybeAudioId) {
          setLastRecordingAudioId(maybeAudioId);
        }
        if (typeof duration === 'number') {
          setRecordingDuration(Math.round(duration));
        }
        setRecordingId(null);
      } catch (_) {
        setRecordingId(null);
      } finally {
        refreshPipeline();
      }
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaStreamRef.current = stream;
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        if (!audioChunksRef.current.length) return;
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        setRecordedAudioBlob(audioBlob);
        const localUrl = URL.createObjectURL(audioBlob);
        if (recordedAudioUrl) {
          URL.revokeObjectURL(recordedAudioUrl);
        }
        setRecordedAudioUrl(localUrl);
        audioChunksRef.current = [];
      };

      const startRes = await pillarCAPI.startRecording();
      setRecordingId(startRes?.data?.recording_id || null);
      setLastRecordingAudioId(null);
      setRecordedAudioBlob(null);
      mediaRecorder.start();
      setIsRecording(true);
      setRecordingDuration(0);
      refreshPipeline();
    } catch (_) {
      setIsRecording(false);
    }
  };

  const handlePlayRecording = async () => {
    if (!recordedAudioUrl && !lastRecordingAudioId) return;
    try {
      setIsPlaying(true);
      if (recordedAudioUrl) {
        const audio = new Audio(recordedAudioUrl);
        await audio.play();
      } else {
        await pillarCAPI.playAudio(lastRecordingAudioId);
      }
    } catch (_) {
      setMessages(prev => [...prev, { isUser: false, text: 'Unable to play recording right now.' }]);
    } finally {
      setIsPlaying(false);
    }
  };

  const blobToBase64 = (blob) => (
    new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onloadend = () => {
        const result = String(reader.result || '');
        const base64 = result.includes(',') ? result.split(',')[1] : result;
        resolve(base64);
      };
      reader.onerror = reject;
      reader.readAsDataURL(blob);
    })
  );

  const speakText = (text) => {
    if (!text || !window?.speechSynthesis) return;
    try {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1;
      utterance.pitch = 1;
      utterance.volume = 1;
      window.speechSynthesis.speak(utterance);
    } catch (_) {
      // ignore browser TTS errors
    }
  };

  const handleSendRecording = async () => {
    if (!recordedAudioBlob) return;
    try {
      setIsSendingVoice(true);
      const audioBase64 = await blobToBase64(recordedAudioBlob);
      const res = await pillarCAPI.sendVoiceMessage(audioBase64);
      const responseText = res?.data?.response_text || 'Processed voice message.';
      const transcript = res?.data?.transcript;
      const bookingPayload = res?.data?.booking;
      const ctx = res?.data?.theme_context;
      setThemeContext({
        topTheme: ctx?.top_theme || null,
        confidence: ctx?.confidence ?? null,
      });
      if (transcript) {
        setMessages((prev) => [...prev, { isUser: true, text: transcript }]);
      } else {
        setMessages((prev) => [...prev, { isUser: true, text: '🎤 Voice message sent' }]);
      }
      setMessages((prev) => [...prev, { isUser: false, text: responseText }]);
      speakText(responseText);
      if (bookingPayload?.booking_code) {
        const d = parseBookingDate(bookingPayload.scheduled_for);
        setBooking({
          code: bookingPayload.booking_code,
          date: d ? d.toLocaleDateString() : '-',
          time: d ? d.toLocaleTimeString() : '-',
          rm: 'Advisor',
          status: bookingPayload.status || 'pending_approval'
        });
        setBookingStatus('confirmed');
        setTimeout(() => refetchActions(), 1000);
      }
      refreshPipeline();
    } catch (e) {
      const errText = e?.response?.data?.detail || 'Failed to send recorded voice.';
      setMessages((prev) => [...prev, { isUser: false, text: errText }]);
    } finally {
      setIsSendingVoice(false);
    }
  };

  const handlePlayAgentTTS = () => {
    const lastAgentMessage = [...messages].reverse().find((msg) => !msg.isUser)?.text;
    if (!lastAgentMessage) return;
    speakText(lastAgentMessage);
  };

  const parseBookingDate = (str) => {
    if (!str) return null;
    const clean = str.replace(/(\+\d{2}:\d{2})Z$/, '$1');
    const d = new Date(clean);
    return isNaN(d.getTime()) ? null : d;
  };

  const handleSend = async () => {
    if (!inputText.trim()) return;
    const userMsg = inputText;
    setMessages(prev => [...prev, { isUser: true, text: userMsg }]);
    setInputText('');

    try {
      const res = await pillarCAPI.sendMessage(userMsg);
      const responseText = res?.data?.response_text || 'Processed.';
      const bookingPayload = res?.data?.booking;
      const ctx = res?.data?.theme_context;
      setThemeContext({
        topTheme: ctx?.top_theme || null,
        confidence: ctx?.confidence ?? null,
      });
      setMessages(prev => [...prev, { isUser: false, text: responseText }]);
      if (inputMode === 'voice') speakText(responseText);
      if (bookingPayload?.booking_code) {
        const d = parseBookingDate(bookingPayload.scheduled_for);
        setBooking({
          code: bookingPayload.booking_code,
          date: d ? d.toLocaleDateString() : '-',
          time: d ? d.toLocaleTimeString() : '-',
          rm: 'Advisor',
          status: bookingPayload.status || 'pending_approval'
        });
        setBookingStatus('confirmed');
        setTimeout(() => refetchActions(), 1000);
      }
      refreshPipeline();
    } catch (e) {
      const errText = e?.response?.data?.detail || 'Failed to send message.';
      setMessages(prev => [...prev, { isUser: false, text: errText }]);
    }
  };

  const pipelineSteps = [
    { id: 'VAD', label: 'VAD', icon: Mic },
    { id: 'STT', label: 'STT', icon: Volume2 },
    { id: 'LLM', label: 'LLM', icon: Bot },
    { id: 'TTS', label: 'TTS', icon: Volume2 },
    { id: 'Calendar', label: 'Calendar', icon: Calendar },
    { id: 'Doc', label: 'Doc', icon: FileText },
    { id: 'Email', label: 'Email', icon: Mail }
  ];

  return (
    <Container>
      <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
      <Header>
        <Title>
          <Wrench size={28} color="#1E3A5F" style={{ marginRight: '8px' }} />
          AI Voice Scheduler
        </Title>
        <PipelineStatus>
          <Wrench size={16} />
          PIPELINE STATUS
          <PipelineSteps>
            {pipelineSteps.map((step, idx) => (
              <Step 
                key={step.id} 
                active={pipelineStatuses[step.id] === 'active'}
                completed={pipelineStatuses[step.id] === 'done'}
              >
                {step.label}
              </Step>
            ))}
          </PipelineSteps>
        </PipelineStatus>
      </Header>

      <ThemesBar>
          <ThemesLabel>Weekly Pulse Themes</ThemesLabel>
          {themesFetching ? (
            <span style={{ fontSize: 13, color: '#5DADE2' }}>Fetching latest themes...</span>
          ) : pulseThemes.length === 0 ? (
            <span style={{ fontSize: 13, color: '#5DADE2' }}>Loading themes...</span>
          ) : (
            pulseThemes.map((t, i) => (
              <ThemeChip key={i}>
                {t.theme}
                <ThemeConfidence>{Math.round((t.confidence || 0) * 100)}%</ThemeConfidence>
              </ThemeChip>
            ))
          )}
          <button
            onClick={() => handleRefreshThemes()}
            disabled={themesFetching}
            style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 6, padding: '6px 14px', border: '2px solid #1E3A5F', borderRadius: 20, background: 'white', color: '#1E3A5F', fontWeight: 600, fontSize: 12, cursor: themesFetching ? 'not-allowed' : 'pointer', opacity: themesFetching ? 0.6 : 1 }}
          >
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" style={{ animation: themesFetching ? 'spin 1s linear infinite' : 'none' }}>
              <path d="M21 12a9 9 0 1 1-6.219-8.56" />
            </svg>
            {themesFetching ? 'Fetching...' : 'Refresh Themes'}
          </button>
        </ThemesBar>

      <MainLayout>
        <Panel>
          <PanelHeader>
            <Mic size={18} />
            Voice Recording Interface
          </PanelHeader>
          <PanelContent>
            <RecordingArea>
              <RecordButton recording={isRecording} onClick={handleRecord}>
                {isRecording ? <Square size={36} /> : <Mic size={36} />}
              </RecordButton>
              <div style={{ fontSize: '24px', fontWeight: '700', color: '#1E3A5F' }}>
                {formatTime(recordingDuration)}
              </div>
              <div style={{ fontSize: '13px', color: '#5DADE2' }}>
                {isRecording ? 'Recording...' : 'Tap to record'}
              </div>
            </RecordingArea>

            <Waveform visible={isRecording} />

            <RecordingControls>
              <ControlButton variant="play" onClick={handlePlayRecording} disabled={isRecording || (!recordedAudioUrl && !lastRecordingAudioId) || isPlaying}>
                <Play size={16} /> Play
              </ControlButton>
              <ControlButton onClick={handleSendRecording} disabled={isRecording || !recordedAudioBlob || isSendingVoice}>
                {isSendingVoice ? 'Sending...' : 'Send Recording'}
              </ControlButton>
              <ControlButton variant="cancel" onClick={async () => {
                if (recordingId) {
                  try { await pillarCAPI.cancelRecording(recordingId); } catch (_) {}
                }
                if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
                  mediaRecorderRef.current.stop();
                }
                if (mediaStreamRef.current) {
                  mediaStreamRef.current.getTracks().forEach((track) => track.stop());
                  mediaStreamRef.current = null;
                }
                if (recordedAudioUrl) {
                  URL.revokeObjectURL(recordedAudioUrl);
                  setRecordedAudioUrl(null);
                }
                setRecordedAudioBlob(null);
                setIsRecording(false);
                setRecordingDuration(0);
                setRecordingId(null);
                setLastRecordingAudioId(null);
                refreshPipeline();
              }} disabled={!isRecording && !recordedAudioBlob && !recordingId}>
                <X size={16} /> Cancel
              </ControlButton>
            </RecordingControls>

            <AgentVoiceSection>
              <AgentVoiceHeader>
                <Volume2 size={16} />
                Agent Voice (TTS Output)
              </AgentVoiceHeader>
              <AgentVoicePlayer>
                <PlayButton onClick={handlePlayAgentTTS} disabled={isPlaying}>
                  <Play size={20} />
                </PlayButton>
                <div style={{ flex: 1, height: '4px', background: '#E8F4FC', borderRadius: '2px', position: 'relative' }}>
                  <div style={{ position: 'absolute', left: 0, top: 0, height: '100%', width: '60%', background: '#5DADE2', borderRadius: '2px' }} />
                </div>
                <span style={{ fontSize: '12px', color: '#5DADE2' }}>0:12</span>
              </AgentVoicePlayer>
            </AgentVoiceSection>
          </PanelContent>
        </Panel>

        <Panel>
          <PanelHeader>
            <Bot size={18} />
            Conversation Chatbot
          </PanelHeader>
          <PanelContent>
            <ChatContainer>
              <MessagesArea>
                {messages.map((msg, idx) => (
                  <Message key={idx} isUser={msg.isUser}>
                    <Avatar isUser={msg.isUser}>
                      {msg.isUser ? <User size={18} /> : <Bot size={18} />}
                    </Avatar>
                    <MessageContent isUser={msg.isUser}>
                      {msg.text}
                    </MessageContent>
                  </Message>
                ))}
                <div ref={messagesEndRef} />
              </MessagesArea>
              

              <InputArea>
                <Input 
                  placeholder="Type your message..."
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                />
                <SendButton onClick={handleSend} disabled={!inputText.trim()}>
                  Send
                </SendButton>
              </InputArea>
              {themeContext.topTheme && (
                <ThemeContextBadge>
                  Theme from Insight-Driven Pulse: {themeContext.topTheme}
                  {themeContext.confidence !== null ? ` (confidence ${themeContext.confidence})` : ''}
                </ThemeContextBadge>
              )}
            </ChatContainer>
          </PanelContent>
        </Panel>

        <Panel>
          <PanelHeader>
            <CheckCircle size={18} />
            Booking Confirmed
          </PanelHeader>
          <PanelContent>
            <BookingCard status={bookingStatus}>
              <BookingHeader status={bookingStatus}>
                <CheckCircle size={20} />
                {bookingStatus === 'confirmed' ? 'Booking Confirmed' : 'Awaiting Confirmation'}
              </BookingHeader>

              <BookingDetail status={bookingStatus}>
                <DetailIcon status={bookingStatus}><FileText size={18} /></DetailIcon>
                <DetailContent>
                  <DetailLabel>Booking Code</DetailLabel>
                  <DetailValue>{booking.code}</DetailValue>
                </DetailContent>
              </BookingDetail>

              <BookingDetail status={bookingStatus}>
                <DetailIcon status={bookingStatus}><Calendar size={18} /></DetailIcon>
                <DetailContent>
                  <DetailLabel>Date</DetailLabel>
                  <DetailValue>{booking.date}</DetailValue>
                </DetailContent>
              </BookingDetail>

              <BookingDetail status={bookingStatus}>
                <DetailIcon status={bookingStatus}><Clock size={18} /></DetailIcon>
                <DetailContent>
                  <DetailLabel>Time</DetailLabel>
                  <DetailValue>{booking.time}</DetailValue>
                </DetailContent>
              </BookingDetail>

              <BookingDetail status={bookingStatus}>
                <DetailIcon status={bookingStatus}><User size={18} /></DetailIcon>
                <DetailContent>
                  <DetailLabel>Relationship Manager</DetailLabel>
                  <DetailValue>{booking.rm}</DetailValue>
                </DetailContent>
              </BookingDetail>

              <BookingDetail status={bookingStatus}>
                <DetailIcon status={bookingStatus}><CheckCircle size={18} /></DetailIcon>
                <DetailContent>
                  <DetailLabel>Status</DetailLabel>
                  <DetailValue>{booking.status}</DetailValue>
                </DetailContent>
              </BookingDetail>
            </BookingCard>


          </PanelContent>
        </Panel>
      </MainLayout>

      <QuickTips>
        <QuickTipsTitle>Quick Use Tips</QuickTipsTitle>
        <QuickTip>Hold the red record button to capture voice input</QuickTip>
        <QuickTip>Switch to text mode if you prefer typing over speaking</QuickTip>
        <QuickTip>Watch the pipeline status bar to track voice processing in real-time</QuickTip>
        <QuickTip>Booking confirmation requires HITL approval from the approval center below</QuickTip>
      </QuickTips>

      <HITLSection>
        <TabBar>
          <Tab active={hitlTab === 'pending'} onClick={() => setHitlTab('pending')}>
            <Clock size={16} /> Pending Approvals {onlyPending.length > 0 && `(${onlyPending.length})`}
          </Tab>
          <Tab active={hitlTab === 'resolved'} onClick={() => setHitlTab('resolved')}>
            <CheckCircle size={16} /> Resolved ({resolvedActions.length})
          </Tab>
        </TabBar>
        <HITLBody>
          <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 12 }}>
            <a
              href="https://docs.google.com/document/d/1PtKhugpyu0W1SBhlHcBqlhpHQ1bJnxm9uh0dr-O5LIU/edit?tab=t.0"
              target="_blank"
              rel="noopener noreferrer"
              style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '8px 16px', border: '2px solid #1E3A5F', borderRadius: 8, background: 'white', color: '#1E3A5F', fontWeight: 600, fontSize: 13, textDecoration: 'none' }}
            >
              <FileText size={15} /> Tracking Doc
            </a>
          </div>
          <StatsGrid>
            <StatCard><StatValue>{onlyPending.length}</StatValue><StatLabel>Pending Approvals</StatLabel></StatCard>
            <StatCard><StatValue>{resolvedActions.length}</StatValue><StatLabel>Resolved</StatLabel></StatCard>
            <StatCard><StatValue>{dedupedActions.length}</StatValue><StatLabel>Total Bookings</StatLabel></StatCard>
          </StatsGrid>

          <HITLLayout>
            <div>
              <Table>
                <thead>
                  <tr>
                    <Th>Booking Code</Th>
                    <Th>Details</Th>
                    <Th>Requested</Th>
                    <Th>Status</Th>
                  </tr>
                </thead>
                <tbody>
                  {(hitlTab === 'pending' ? onlyPending : resolvedActions).length === 0 && (
                    <tr><Td colSpan={4} style={{ textAlign: 'center', color: '#5DADE2' }}>No actions.</Td></tr>
                  )}
                  {(hitlTab === 'pending' ? onlyPending : resolvedActions).map(action => (
                    <Tr key={action.id} selected={selectedAction === action.id} onClick={() => setSelectedAction(action.id)}>
                      <Td><BookingCode>{action.booking_code}</BookingCode></Td>
                      <Td>{action.details?.subject || action.details?.datetime || '-'}</Td>
                      <Td>{action.requested_at ? new Date(action.requested_at).toLocaleString() : '-'}</Td>
                      <Td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                          <StatusBadge status={action.status}><Clock size={11} />{action.status}</StatusBadge>
                          {action.status === 'pending' && (
                            <button
                              onClick={e => { e.stopPropagation(); handleHITLApprove(action.id); }}
                              style={{ padding: '3px 10px', fontSize: 11, fontWeight: 600, border: '1.5px solid #27AE60', borderRadius: 12, background: '#E8FCF0', color: '#27AE60', cursor: 'pointer', whiteSpace: 'nowrap' }}
                            >
                              ✓ Mark Done
                            </button>
                          )}
                        </div>
                      </Td>
                    </Tr>
                  ))}
                </tbody>
              </Table>
            </div>

            <EmailPreviewCard>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16, paddingBottom: 14, borderBottom: '2px solid #E8F4FC' }}>
                <div style={{ width: 40, height: 40, background: '#E8F4FC', borderRadius: 8, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#1E3A5F' }}>
                  <Mail size={20} />
                </div>
                <div>
                  <div style={{ fontWeight: 600, color: '#1E3A5F', fontSize: 15 }}>Preview Draft Email</div>
                  <div style={{ fontSize: 13, color: '#5DADE2' }}>Booking: <BookingCode>{selectedBookingCode || '-'}</BookingCode></div>
                </div>
              </div>
              <ContextBanner>
                <AlertTriangle size={15} color="#E67E22" />
                Includes Weekly Pulse market context
              </ContextBanner>
              <EmailLabel>Subject</EmailLabel>
              <EmailInput value={emailDraft.subject} onChange={e => setEmailDraft({ ...emailDraft, subject: e.target.value })} readOnly={!isEditing} />
              <EmailLabel>Body</EmailLabel>
              <EmailTextArea value={emailDraft.body} onChange={e => setEmailDraft({ ...emailDraft, body: e.target.value })} readOnly={!isEditing} />
              <PreviewActions>
              </PreviewActions>
            </EmailPreviewCard>
          </HITLLayout>
        </HITLBody>
      </HITLSection>
    </Container>
  );
};

export default PillarC;
