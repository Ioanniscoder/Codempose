# Creating a Standalone Codempose Executable

## Overview
This guide explains how to convert the Codempose Python system into a standalone executable that can be distributed and run without requiring Python installation.

## Tarball Contents
**File:** `backup/codempose_multivoice_shorthand.tar.gz` (181KB)

**Includes:**
- Core modules (project_template, music_data, lilypond_parser, etc.)
- Study files (first.py through seventh.py)
- Composition shorthand system (composition_shorthand.py)
- All parser modules (lily_tokenizer, lily_token_parser, lily_to_tiny, etc.)
- Documentation (all .md files)
- Example outputs (sixth.*, seventh.*)
- requirements.txt

## Method 1: PyInstaller (Recommended)

### What is PyInstaller?
PyInstaller bundles a Python application and all its dependencies into a single executable.

### Installation
```bash
pip install pyinstaller
```

### Basic Usage - Single Study File

#### Create executable for seventh.py:
```bash
pyinstaller --onefile \
  --name=codempose-seventh \
  --add-data="*.py:." \
  seventh.py
```

**Result:** `dist/codempose-seventh` (or `codempose-seventh.exe` on Windows)

**Usage:**
```bash
./dist/codempose-seventh
# Generates outputs/seventh.{ly,pdf,midi}
```

### Advanced Usage - Complete System

#### Create a launcher script:
```bash
# File: codempose_launcher.py

import sys
import os
from pathlib import Path

def main():
    """
    Standalone launcher for Codempose.
    
    Usage:
        codempose <study_file.py>
        codempose sixth.py
        codempose seventh.py
    """
    if len(sys.argv) < 2:
        print("Usage: codempose <study_file.py>")
        print("\nAvailable studies:")
        print("  first.py - Basic two-staff composition")
        print("  sixth.py - Multi-voice polyphony (manual chaining)")
        print("  seventh.py - Multi-voice polyphony (shorthand)")
        sys.exit(1)
    
    study_file = sys.argv[1]
    
    if not Path(study_file).exists():
        print(f"Error: {study_file} not found")
        sys.exit(1)
    
    # Import and run
    from project_template import run_pipeline_from_file
    run_pipeline_from_file(study_file)

if __name__ == '__main__':
    main()
```

#### Build complete executable:
```bash
pyinstaller --onefile \
  --name=codempose \
  --add-data="project_template.py:." \
  --add-data="music_data.py:." \
  --add-data="lilypond_parser.py:." \
  --add-data="lily_tokenizer.py:." \
  --add-data="lily_token_parser.py:." \
  --add-data="lily_to_tiny.py:." \
  --add-data="relative_octave_logic.py:." \
  --add-data="data_structures.py:." \
  --add-data="composition_shorthand.py:." \
  --hidden-import=music21 \
  --hidden-import=abjad \
  codempose_launcher.py
```

**Usage:**
```bash
./dist/codempose seventh.py
./dist/codempose sixth.py
```

### Platform-Specific Notes

#### Linux/macOS:
```bash
pyinstaller --onefile seventh.py
# Result: dist/seventh (no extension)
chmod +x dist/seventh
./dist/seventh
```

#### Windows:
```bash
pyinstaller --onefile seventh.py
# Result: dist\seventh.exe
seventh.exe
```

## Method 2: Nuitka (Faster Execution)

### What is Nuitka?
Nuitka compiles Python to C code, resulting in faster execution than PyInstaller.

### Installation
```bash
pip install nuitka
```

### Build standalone executable:
```bash
nuitka --standalone \
  --onefile \
  --output-dir=dist \
  --include-module=music21 \
  --include-module=abjad \
  seventh.py
```

**Result:** `dist/seventh.bin` (Linux/macOS) or `dist/seventh.exe` (Windows)

## Method 3: Shiv (Python Zipapp)

### What is Shiv?
Creates a self-contained Python zipapp with dependencies bundled.

### Installation
```bash
pip install shiv
```

### Build zipapp:
```bash
# Install dependencies to a directory
pip install --target deps music21 abjad

# Create zipapp
shiv --site-packages deps \
  --output-file codempose.pyz \
  --entry-point seventh:main \
  seventh.py project_template.py music_data.py lilypond_parser.py \
  lily_tokenizer.py lily_token_parser.py lily_to_tiny.py \
  relative_octave_logic.py data_structures.py composition_shorthand.py
```

**Usage:**
```bash
python3 codempose.pyz
```

## Method 4: Docker Container (Cross-Platform)

### Create Dockerfile:
```dockerfile
FROM python:3.11-slim

# Install LilyPond
RUN apt-get update && \
    apt-get install -y lilypond && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy Codempose files
COPY *.py /app/
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create outputs directory
RUN mkdir -p /app/outputs

# Entry point
ENTRYPOINT ["python3"]
CMD ["seventh.py"]
```

### Build and run:
```bash
# Build image
docker build -t codempose .

# Run seventh.py
docker run -v $(pwd)/outputs:/app/outputs codempose seventh.py

# Run sixth.py
docker run -v $(pwd)/outputs:/app/outputs codempose sixth.py
```

## Recommended Approach for Codempose

### Option A: Study-Specific Executables
Best for distributing individual compositions:

```bash
# Create executable for seventh.py
pyinstaller --onefile \
  --name=seventh-study \
  --add-data="project_template.py:." \
  --add-data="music_data.py:." \
  --add-data="lilypond_parser.py:." \
  --add-data="lily_tokenizer.py:." \
  --add-data="lily_token_parser.py:." \
  --add-data="lily_to_tiny.py:." \
  --add-data="relative_octave_logic.py:." \
  --add-data="data_structures.py:." \
  --add-data="composition_shorthand.py:." \
  --hidden-import=music21 \
  --hidden-import=abjad \
  seventh.py

# Result: dist/seventh-study
# User runs: ./seventh-study
# Generates: outputs/seventh.{ly,pdf,midi}
```

**Advantages:**
- Single file distribution
- No Python required on target machine
- LilyPond still required (for PDF/MIDI generation)
- Each study is independent

### Option B: Universal Codempose Launcher
Best for developers who want to run any study file:

```bash
# Create codempose_cli.py (command-line interface)
# Build with all modules included
pyinstaller --onefile \
  --name=codempose \
  --add-data="*.py:." \
  --hidden-import=music21 \
  --hidden-import=abjad \
  codempose_cli.py

# User runs: ./codempose seventh.py
```

### Option C: Docker Image (Most Complete)
Best for complete cross-platform distribution with LilyPond included:

```bash
# Build once
docker build -t codempose:latest .

# Distribute image
docker save codempose:latest | gzip > codempose_docker.tar.gz

# User loads and runs
docker load < codempose_docker.tar.gz
docker run -v $(pwd)/outputs:/app/outputs codempose:latest seventh.py
```

## Requirements for Target Systems

### For PyInstaller/Nuitka Executables:
- **NOT REQUIRED:** Python installation
- **REQUIRED:** LilyPond (for PDF/MIDI generation)
- **REQUIRED:** System libraries (glibc on Linux, Visual C++ on Windows)

### For Docker:
- **REQUIRED:** Docker runtime
- **NOT REQUIRED:** Python, LilyPond (all bundled in image)

## Distribution Checklist

### Minimum Distribution Package:
```
codempose_standalone/
├── codempose              # Executable (PyInstaller output)
├── README.md              # Usage instructions
├── examples/
│   ├── sixth.py           # Example study files
│   ├── seventh.py
│   └── my_composition.py  # User can add their own
└── requirements.txt       # For reference only
```

### Complete Distribution Package:
```
codempose_complete/
├── bin/
│   └── codempose          # Executable
├── docs/
│   ├── README_DOCUMENTATION.md
│   ├── VOICE_CHAINING_GUIDE.md
│   └── COMPOSITION_SHORTHAND_PROPOSAL.md
├── examples/
│   ├── first.py
│   ├── sixth.py
│   ├── seventh.py
│   └── templates/
│       └── composition_template.py
├── source/                # Optional: include source if open-source
│   └── *.py
└── LICENSE
```

## Example Build Script

Create `build_standalone.sh`:

```bash
#!/bin/bash
# Build standalone Codempose executable

echo "🔨 Building Codempose standalone executable..."

# Clean previous builds
rm -rf build/ dist/ *.spec

# Build with PyInstaller
pyinstaller --onefile \
  --name=codempose \
  --add-data="project_template.py:." \
  --add-data="music_data.py:." \
  --add-data="lilypond_parser.py:." \
  --add-data="lily_tokenizer.py:." \
  --add-data="lily_token_parser.py:." \
  --add-data="lily_to_tiny.py:." \
  --add-data="relative_octave_logic.py:." \
  --add-data="data_structures.py:." \
  --add-data="composition_shorthand.py:." \
  --hidden-import=music21 \
  --hidden-import=abjad \
  --hidden-import=fractions \
  --hidden-import=pathlib \
  seventh.py

echo "✅ Build complete: dist/codempose"
echo ""
echo "📋 Test the executable:"
echo "  ./dist/codempose"
echo ""
echo "📦 To distribute:"
echo "  1. Copy dist/codempose to target system"
echo "  2. Ensure LilyPond is installed on target"
echo "  3. Run: ./codempose"
```

## Testing the Executable

```bash
# Build
./build_standalone.sh

# Test
cd dist/
./codempose

# Should generate:
# outputs/seventh.ly
# outputs/seventh.pdf
# outputs/seventh.midi
```

## Troubleshooting

### "Module not found" errors:
```bash
# Add missing modules with --hidden-import
pyinstaller --hidden-import=missing_module seventh.py
```

### Large executable size:
```bash
# Use UPX compression
pyinstaller --onefile --upx-dir=/path/to/upx seventh.py
```

### Dynamic imports not working:
```bash
# Add all modules explicitly
pyinstaller --onefile \
  --collect-all music21 \
  --collect-all abjad \
  seventh.py
```

## Summary

**Recommended for Codempose:**

1. **Development:** Use Python directly (`python3 seventh.py`)
2. **Distribution:** Use PyInstaller for standalone executables
3. **Cross-platform:** Use Docker for complete isolation

**Quick Start:**
```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller --onefile seventh.py

# Test
./dist/seventh

# Distribute
cp dist/seventh /path/to/distribution/
```

The executable will work on any system with the same OS/architecture, requiring only LilyPond for final PDF/MIDI generation.
