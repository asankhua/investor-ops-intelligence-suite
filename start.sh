#!/bin/bash
# Export all env vars so supervisord child processes inherit them
export PINECONE_API_KEY=${PINECONE_API_KEY:-}
export PINECONE_INDEX_NAME=${PINECONE_INDEX_NAME:-investor-kb}
export PINECONE_CLOUD=${PINECONE_CLOUD:-aws}
export PINECONE_REGION=${PINECONE_REGION:-us-east-1}
export OPENROUTER_API_KEY=${OPENROUTER_API_KEY:-}
export OPENROUTER_BASE_URL=${OPENROUTER_BASE_URL:-https://openrouter.ai/api/v1}
export OPENROUTER_CHAT_MODEL=${OPENROUTER_CHAT_MODEL:-openai/gpt-4o}
export EMBEDDING_MODEL=${EMBEDDING_MODEL:-openai/text-embedding-3-large}
export EMBEDDING_DIMENSION=${EMBEDDING_DIMENSION:-3072}
export GROQ_API_KEY=${GROQ_API_KEY:-}
export GROQ_BASE_URL=${GROQ_BASE_URL:-https://api.groq.com/openai/v1}
export SARVAM_API_KEY=${SARVAM_API_KEY:-}
export SARVAM_BASE_URL=${SARVAM_BASE_URL:-https://api.sarvam.ai}
export MCP_SERVER_URL=${MCP_SERVER_URL:-https://ashishsankhua-google-docs-gmail-mcp-server.hf.space}
export MCP_EMAIL_SERVER_URL=${MCP_EMAIL_SERVER_URL:-https://ashishsankhua-google-docs-gmail-mcp-server.hf.space}
export MCP_TIMEOUT_S=${MCP_TIMEOUT_S:-10}
export GOOGLE_TRACKING_DOC_ID=${GOOGLE_TRACKING_DOC_ID:-}
export GOOGLE_TOKEN_JSON=${GOOGLE_TOKEN_JSON:-}
export ADVISOR_EMAIL=${ADVISOR_EMAIL:-}
export GOOGLE_MEET_URL=${GOOGLE_MEET_URL:-}
export WEEKLY_PULSE_WORD_LIMIT=${WEEKLY_PULSE_WORD_LIMIT:-250}
export WEEKLY_PULSE_ACTION_COUNT=${WEEKLY_PULSE_ACTION_COUNT:-3}
export PHASE1_BASE_URL=http://localhost:8101
export PHASE2_BASE_URL=http://localhost:8102
export PHASE3_BASE_URL=http://localhost:8103

exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
