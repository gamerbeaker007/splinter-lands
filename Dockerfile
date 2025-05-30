# syntax=docker/dockerfile:1

FROM python:3.12-slim-bullseye

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY src /app/src
COPY .streamlit/config.toml /app/.streamlit/config.toml
COPY .streamlit/pages.toml /app/.streamlit/pages.toml
COPY main.py /app/main.py

# temporary
COPY alembic /app/alembic
COPY alembic.ini /app/alembic.ini


# Define a build-arg for APP_VERSION
ARG APP_VERSION

# Set the environment variable for the app version
ENV APP_VERSION=$APP_VERSION
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8501

# Run Streamlit
CMD ["streamlit", "run", "main.py", "--server.port=8501"]
