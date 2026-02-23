# Use slim Python image
FROM python:3.10

# Set working directory
WORKDIR /app

# Install system dependencies (needed for torch sometimes)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files first (for caching)
COPY pyproject.toml uv.lock ./

# Install uv
RUN pip install uv

# Install dependencies
RUN uv sync --no-dev

# Copy application code
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Run server
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]