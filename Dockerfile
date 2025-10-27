# Multi-stage build for smaller image
FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY api/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final stage
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 acmeapi && \
    mkdir -p /app/api/data && \
    chown -R acmeapi:acmeapi /app

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /home/acmeapi/.local

# Copy application code
COPY --chown=acmeapi:acmeapi api/ ./api/
COPY --chown=acmeapi:acmeapi dashboard/ ./dashboard/

# Switch to non-root user
USER acmeapi

# Add .local/bin to PATH
ENV PATH=/home/acmeapi/.local/bin:$PATH

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/healthcheck || exit 1

# Run the application
CMD ["python", "api/main.py"]