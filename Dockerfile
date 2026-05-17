# Stage 1: Build Frontend (Next.js)
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

# Copy frontend package files and install dependencies
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install

# Copy the rest of the frontend code and build static export
COPY frontend/ ./
RUN npm run build

# Stage 2: Build Backend (FastAPI) and Serve
FROM python:3.11-slim
WORKDIR /app

# Install backend dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/main.py .

# Copy built frontend static files from Stage 1 into backend's static folder
COPY --from=frontend-builder /app/frontend/out ./static

# Expose port 8080 (Cloud Run default)
EXPOSE 8080

# Run FastAPI server with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
