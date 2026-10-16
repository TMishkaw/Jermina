# Headless Remotion Video Renderer with Chromium & FFmpeg
FROM node:22-bookworm-slim

# Install system dependencies required for headless Chromium & audio/video rendering
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    ffmpeg \
    fonts-noto-color-emoji \
    fonts-freefont-ttf \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Tell Remotion and Puppeteer to use installed Chromium
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true \
    PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium \
    REMOTION_CHROMIUM_EXECUTABLE_PATH=/usr/bin/chromium

WORKDIR /app

COPY package*.json ./
RUN npm ci --omit=dev || npm install

COPY . .

# Default command: render Stickman Short
ENTRYPOINT ["npx", "remotion", "render", "src/index.ts", "StickmanShort9x16"]
CMD ["out/video.mp4"]
