#!/bin/bash
# Strip trailing newlines from all HF secrets and export
strip() { echo -n "${1}" | tr -d '\n\r'; }

export PINECONE_API_KEY=$(strip "${PINECONE_API_KEY}")
export PINECONE_INDEX_NAME=$(strip "${PINECONE_INDEX_NAME:-investor-kb}")
export PINECONE_CLOUD=$(strip "${PINECONE_CLOUD:-aws}")
export PINECONE_REGION=$(strip "${PINECONE_REGION:-us-east-1}")
export OPENROUTER_API_KEY=$(strip "${OPENROUTER_API_KEY}")
export OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
export OPENROUTER_CHAT_MODEL=$(strip "${OPENROUTER_CHAT_MODEL:-openai/gpt-4o}")
export EMBEDDING_MODEL=$(strip "${EMBEDDING_MODEL:-openai/text-embedding-3-large}")
export EMBEDDING_DIMENSION=$(strip "${EMBEDDING_DIMENSION:-3072}")
export GROQ_API_KEY=$(strip "${GROQ_API_KEY}")
export GROQ_BASE_URL=https://api.groq.com/openai/v1
export SARVAM_API_KEY=$(strip "${SARVAM_API_KEY}")
export SARVAM_BASE_URL=https://api.sarvam.ai
export MCP_SERVER_URL=$(strip "${MCP_SERVER_URL:-https://ashishsankhua-google-docs-gmail-mcp-server.hf.space}")
export MCP_EMAIL_SERVER_URL=$(strip "${MCP_EMAIL_SERVER_URL:-https://ashishsankhua-google-docs-gmail-mcp-server.hf.space}")
export MCP_TIMEOUT_S=$(strip "${MCP_TIMEOUT_S:-10}")
export GOOGLE_TRACKING_DOC_ID=$(strip "${GOOGLE_TRACKING_DOC_ID}")
export GOOGLE_TOKEN_JSON=$(strip "${GOOGLE_TOKEN_JSON}")
export ADVISOR_EMAIL=$(strip "${ADVISOR_EMAIL}")
export GOOGLE_MEET_URL=$(strip "${GOOGLE_MEET_URL}")
export WEEKLY_PULSE_WORD_LIMIT=$(strip "${WEEKLY_PULSE_WORD_LIMIT:-250}")
export WEEKLY_PULSE_ACTION_COUNT=$(strip "${WEEKLY_PULSE_ACTION_COUNT:-3}")
export PHASE1_BASE_URL=http://localhost:8101
export PHASE2_BASE_URL=http://localhost:8102
export PHASE3_BASE_URL=http://localhost:8103

echo "=== ENV CHECK ==="
echo "PINECONE_API_KEY set: $([ -n "$PINECONE_API_KEY" ] && echo YES || echo NO)"
echo "OPENROUTER_API_KEY set: $([ -n "$OPENROUTER_API_KEY" ] && echo YES || echo NO)"
echo "GROQ_API_KEY set: $([ -n "$GROQ_API_KEY" ] && echo YES || echo NO)"
echo "MCP_SERVER_URL: $MCP_SERVER_URL"
echo "================="

exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
