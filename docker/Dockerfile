# Pull official image with Python 3.11.12 slim
FROM python:3.11.12-slim
# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set environment variables to prevent Python from creating .pyc files and to ensure output is unbuffered
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /src

COPY src /src

# Copy the dependency files (pyproject.toml and uv.lock)
COPY pyproject.toml /src/
COPY uv.lock /src/

ENV UV_SYSTEM_PYTHON "true"
ENV UV_PYTHON_PREFERENCE "only-system"

RUN ["uv", "venv", "--system-site-packages", ".venv"]

RUN ["uv", "sync", "--frozen"]

# Enable venv
ENV PATH="/src/.venv/bin:$PATH"

# Command to run the application using uv
ENTRYPOINT ["uv", "run", "--frozen", "python", "/src/tado_autoassist.py"]