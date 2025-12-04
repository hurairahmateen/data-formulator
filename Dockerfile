# Frontend build stage
FROM node:18-alpine AS frontend-build
WORKDIR /app

COPY package.json yarn.lock ./
COPY index.html .
COPY vite.config.ts .
COPY src ./src
COPY public ./public

RUN yarn install --frozen-lockfile
RUN yarn build

# -------------------------------
# Backend (Python / Flask)
# -------------------------------
FROM python:3.11-slim
WORKDIR /app

# Optional: system packages if needed later
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY py-src/ py-src/

# Let Python see py-src as a package root
ENV PYTHONPATH=/app/py-src

# Copy built frontend into backend dist folder
COPY --from=frontend-build /app/py-src/data_formulator/dist ./py-src/data_formulator/dist/

# Expose backend port
EXPOSE 5000

# Run the package's __main__.py (uses run_app())
CMD ["python", "-m", "data_formulator"]
