# Use Python 3.12 slim image
FROM python:3.12-slim

# Create user with UID 1000 (Hugging Face requirement)
RUN useradd -m -u 1000 user

# Switch to user
USER user

# Set environment variables
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PYTHONUNBUFFERED=1

# Set working directory
WORKDIR $HOME/app

# Copy requirements first for Docker layer caching
COPY --chown=user agent_travel/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY --chown=user agent_travel/*.py .
COPY --chown=user agent_travel/*.csv .
COPY --chown=user agent_travel/test_*.json .

# Expose Streamlit port (Hugging Face standard)
EXPOSE 7860

# Health check for container status
HEALTHCHECK CMD curl --fail http://localhost:7860/_stcore/health || exit 1

# Run Streamlit application
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=7860", "--server.address=0.0.0.0", "--server.headless=true"]