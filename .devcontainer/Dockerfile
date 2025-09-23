# Base image for the Python devcontainer
FROM mcr.microsoft.com/devcontainers/python:1-3.11
# Ensure container processes use a UTF-8 English-compatible locale by default.
# This helps tools and scripts inside the container have predictable locale behavior.
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
# Install small set of build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    lilypond \
    git-lfs \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Initialize git-lfs during image build so Codespaces users have it available
RUN git lfs install || true
