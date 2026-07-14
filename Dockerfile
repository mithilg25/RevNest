# ============================================
# BUILD STAGE
# ============================================
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install requirements (layer caching: code changes won't invalidate)
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# ============================================
# RUNTIME STAGE
# ============================================
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies (curl for healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 appuser

# Copy Python packages from builder
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local

# Set environment variables
ENV PATH=/home/appuser/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Copy application code
COPY --chown=appuser:appuser train.py .
COPY --chown=appuser:appuser src/ src/
COPY --chown=appuser:appuser models/ models/
COPY --chown=appuser:appuser artifacts/ artifacts/

# Switch to non-root user
USER appuser

# Expose API port
EXPOSE 8000

# Healthcheck using curl (fixed)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/docs || exit 1

# Run the API server
CMD ["python", "-m", "uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
