FROM python:3.12-slim AS builder 

WORKDIR /backend

RUN apt-get update && \
    apt-get install -y libpq-dev gcc

# Create the virutal env
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# operational stage
FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy the rest of the application
COPY ./app /app
COPY main.py main.py

# Set environment variables
ENV HOST=0.0.0.0
ENV PORT=8080

# Expose the port
EXPOSE ${PORT}

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]