FROM python:3.11-slim

# Install Node.js, nginx, supervisor
RUN apt-get update && apt-get install -y \
    curl nginx supervisor \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies for all phases
COPY phase1_knowledgeBase/requirements.txt /tmp/req1.txt
COPY phase2_weeklyPulse/requirements.txt /tmp/req2.txt
COPY phase3_voiceScheduler/requirements.txt /tmp/req3.txt
COPY phase4_integrationHub/requirements.txt /tmp/req4.txt
RUN pip install --no-cache-dir \
    -r /tmp/req1.txt \
    -r /tmp/req2.txt \
    -r /tmp/req3.txt \
    -r /tmp/req4.txt

# Build React frontend
COPY phase5_frontend/package.json ./phase5_frontend/package.json
RUN npm install --prefix phase5_frontend --silent
COPY phase5_frontend/ ./phase5_frontend/
# Build with empty gateway URL so nginx proxy handles routing
RUN REACT_APP_API_GATEWAY_URL="" REACT_APP_API_VERSION="v1" npm run build --prefix phase5_frontend

# Copy all source
COPY . .

# Nginx config
COPY nginx.conf /etc/nginx/nginx.conf

# Supervisor config
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 7860

COPY start.sh /start.sh
RUN chmod +x /start.sh

CMD ["/start.sh"]
