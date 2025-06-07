# syntax=docker/dockerfile:1

FROM python:3.12-slim-bullseye

WORKDIR /app

# Create .streamlit folder to avoid mount issue
RUN mkdir -p /app/.streamlit

# Install dependencies
COPY requirements.txt ./
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY src /app/src
COPY .streamlit/config.toml /app/.streamlit/config.toml
COPY .streamlit/pages.toml /app/.streamlit/pages.toml
COPY main.py /app/main.py

# Optional: APP_VERSION build argument and env var
ARG APP_VERSION
ENV APP_VERSION=$APP_VERSION
ENV PYTHONUNBUFFERED=1

# Expose Streamlit port
EXPOSE 8501

# Run Streamlit
CMD ["streamlit", "run", "main.py", "--server.port=8501"]
