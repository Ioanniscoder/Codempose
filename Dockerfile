# Codempose - Musical Composition Framework
# Includes Python 3.11, LilyPond, and all dependencies

FROM python:3.11-slim-bookworm

# Metadata
LABEL maintainer="Codempose Project"
LABEL description="Blueprint String Framework for Musical Composition"
LABEL version="1.0"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # LilyPond for music engraving
    lilypond \
    # MIDI playback (optional)
    timidity \
    # Version control
    git \
    # Utilities
    curl \
    wget \
    # Cleanup
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set working directory
WORKDIR /codempose

# Copy requirements first (for layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy Codempose source code
COPY generate_study.py .
COPY CODEMPOSE_STUDY_TEMPLATES.py .
COPY README.md .
COPY src/ ./src/
COPY studies/ ./studies/
COPY tests/ ./tests/
COPY outputs/ ./outputs/

# Set Python path
ENV PYTHONPATH=/codempose/src
ENV PYTHONUNBUFFERED=1

# Create volume mount points
VOLUME ["/codempose/studies", "/codempose/outputs"]

# Default working directory for user sessions
WORKDIR /codempose

# Default command: interactive bash
CMD ["/bin/bash"]

# Usage:
# docker build -t codempose:latest .
# docker run -it -v $(pwd)/my-studies:/codempose/studies codempose:latest
# Then inside container:
#   python generate_study.py 1 "My Study"
#   python studies/first.py
#   ls outputs/
