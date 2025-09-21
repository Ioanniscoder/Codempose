FROM mcr.microsoft.com/devcontainers/python:1-3.11

# Install small set of build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*
