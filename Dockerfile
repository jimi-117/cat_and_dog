FROM python:3.11-slim

WORKDIR /app

# Python dependencies
COPY pyproject.toml .
RUN pip install uv && \
    uv pip install ".[dev]"

# Application code
COPY . .

# Expose ports
EXPOSE 5000 8000

# Start services
CMD ["python", "-m", "src.app.main"]