FROM node:20-alpine

WORKDIR /app

ENV NEXT_TELEMETRY_DISABLED=1

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies (package-lock.json is optional)
RUN npm ci --legacy-peer-deps || npm install --legacy-peer-deps

# Copy all source files
COPY . .

# Build the Next.js app
RUN npm run build

EXPOSE 3000

CMD ["npm", "run", "start"]


