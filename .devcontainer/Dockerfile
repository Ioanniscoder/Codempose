FROM mcr.microsoft.com/devcontainers/python:1-3.11

# Install small set of build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    lilypond \
    git-lfs \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Initialize git-lfs during image build so Codespaces users have it available
RUN git lfs install || true
