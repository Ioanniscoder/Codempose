# Codempose Distribution Guide

**Creating a Portable Distribution with Python and LilyPond**

---

## 🎯 DISTRIBUTION OPTIONS

### Option 1: Docker Container (RECOMMENDED) ⭐
**Best for**: Cross-platform distribution, consistent environment  
**Size**: ~2-3 GB (full environment)  
**Pros**: Works everywhere, includes all dependencies  
**Cons**: Requires Docker installed

### Option 2: Conda Environment
**Best for**: Python users, researchers  
**Size**: ~1-2 GB  
**Pros**: Easy to install, manages dependencies  
**Cons**: Requires Conda/Miniconda

### Option 3: Standalone Python + LilyPond Bundle
**Best for**: End users, minimal setup  
**Size**: ~500 MB - 1 GB  
**Pros**: Simple extraction and run  
**Cons**: Platform-specific builds

### Option 4: Python Wheel + Instructions
**Best for**: Developers, existing Python environments  
**Size**: ~50 MB (Codempose only)  
**Pros**: Minimal size, pip installable  
**Cons**: Users must install Python + LilyPond separately

---

## 📦 OPTION 1: Docker Container (RECOMMENDED)

### Why Docker?
- ✅ **Cross-platform**: Works on Linux, macOS, Windows
- ✅ **Complete environment**: Python, LilyPond, all dependencies included
- ✅ **Reproducible**: Same environment everywhere
- ✅ **No conflicts**: Isolated from host system

### Create Dockerfile

```dockerfile
# Dockerfile
FROM python:3.11-slim-bookworm

# Install system dependencies
RUN apt-get update && apt-get install -y \
    lilypond \
    timidity \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /codempose

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy Codempose files
COPY . .

# Set environment
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/codempose/src

# Default command
CMD ["/bin/bash"]

# Or run a study directly:
# CMD ["python", "studies/first.py"]
```

### Create requirements.txt

```text
abjad==3.19
music21==9.1.0
python-ly==0.9.7
```

### Build and Distribute

```bash
# Build the image
docker build -t codempose:latest .

# Save to tarball
docker save codempose:latest | gzip > codempose-docker.tar.gz

# Distribution size: ~1.5-2 GB
```

### User Installation

```bash
# Load the image
docker load < codempose-docker.tar.gz

# Run interactively
docker run -it -v $(pwd)/my-studies:/codempose/studies codempose:latest

# Generate a study
python generate_study.py 1 "My First Study"

# Run a study
python studies/first.py

# View outputs (mounted volume makes them accessible on host)
```

---

## 📦 OPTION 2: Conda Environment

### Create environment.yml

```yaml
name: codempose
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.11
  - lilypond=2.24
  - pip
  - pip:
    - abjad==3.19
    - music21==9.1.0
    - python-ly==0.9.7
```

### Package the Environment

```bash
# Create the environment
conda env create -f environment.yml

# Activate and pack
conda activate codempose
conda pack -n codempose -o codempose-env.tar.gz

# Distribution size: ~1-2 GB
```

### User Installation

```bash
# Extract environment
mkdir -p ~/miniconda3/envs/codempose
tar -xzf codempose-env.tar.gz -C ~/miniconda3/envs/codempose

# Activate
conda activate codempose

# Extract Codempose files
tar -xzf codempose-release-YYYYMMDD.tar.gz
cd Codempose

# Run
python generate_study.py 1 "My Study"
python studies/first.py
```

---

## 📦 OPTION 3: Standalone Bundle (Platform-Specific)

### For Linux (AppImage or Tarball)

#### Create Portable Python Bundle

```bash
#!/bin/bash
# build-linux-bundle.sh

# Download Python standalone build
wget https://github.com/indygreg/python-build-standalone/releases/download/20231002/cpython-3.11.6+20231002-x86_64-unknown-linux-gnu-install_only.tar.gz

# Extract
tar -xzf cpython-3.11.6*.tar.gz -C portable-python

# Install dependencies
portable-python/python/bin/python3 -m pip install abjad music21 python-ly

# Download LilyPond
wget http://lilypond.org/download/binaries/linux-64/lilypond-2.24.3-linux-x86_64.tar.gz
tar -xzf lilypond-2.24.3*.tar.gz

# Create bundle structure
mkdir -p codempose-bundle
cp -r portable-python codempose-bundle/
cp -r lilypond-2.24.3 codempose-bundle/lilypond
cp -r Codempose/* codempose-bundle/

# Create launcher script
cat > codempose-bundle/codempose.sh << 'EOF'
#!/bin/bash
BUNDLE_DIR="$(cd "$(dirname "$0")" && pwd)"
export PATH="$BUNDLE_DIR/portable-python/python/bin:$BUNDLE_DIR/lilypond/bin:$PATH"
export PYTHONPATH="$BUNDLE_DIR/src"

cd "$BUNDLE_DIR"
python/bin/python3 "$@"
EOF

chmod +x codempose-bundle/codempose.sh

# Package
tar -czf codempose-linux-x86_64.tar.gz codempose-bundle/

# Distribution size: ~500 MB - 800 MB
```

#### User Installation (Linux)

```bash
# Extract bundle
tar -xzf codempose-linux-x86_64.tar.gz
cd codempose-bundle

# Run
./codempose.sh generate_study.py 1 "My Study"
./codempose.sh studies/first.py

# Add to PATH (optional)
echo 'export PATH="'$(pwd)'":$PATH' >> ~/.bashrc
```

---

### For macOS (App Bundle)

```bash
#!/bin/bash
# build-macos-bundle.sh

# Download Python for macOS
# Use official python.org installer or python-build-standalone

# Install dependencies
python3 -m pip install --target=./python-libs abjad music21 python-ly

# Download LilyPond for macOS
# http://lilypond.org/macos-x.html
# LilyPond-2.24.3-darwin-x86_64.tar.gz

# Create .app bundle structure
mkdir -p Codempose.app/Contents/{MacOS,Resources,Frameworks}

# Copy files
cp -r Codempose/* Codempose.app/Contents/Resources/
cp -r python-libs Codempose.app/Contents/Frameworks/
cp -r LilyPond.app Codempose.app/Contents/Frameworks/

# Create launcher
cat > Codempose.app/Contents/MacOS/codempose << 'EOF'
#!/bin/bash
BUNDLE="$(cd "$(dirname "$0")/../" && pwd)"
export PYTHONPATH="$BUNDLE/Frameworks/python-libs:$BUNDLE/Resources/src"
export PATH="$BUNDLE/Frameworks/LilyPond.app/Contents/Resources/bin:$PATH"

cd "$BUNDLE/Resources"
python3 "$@"
EOF

chmod +x Codempose.app/Contents/MacOS/codempose

# Create Info.plist
cat > Codempose.app/Contents/Info.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>codempose</string>
    <key>CFBundleName</key>
    <string>Codempose</string>
    <key>CFBundleIdentifier</key>
    <string>org.codempose</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
</dict>
</plist>
EOF

# Create DMG
hdiutil create -volname "Codempose" -srcfolder Codempose.app -ov -format UDZO codempose-macos.dmg
```

---

### For Windows (Portable EXE + Installer)

```bash
# Use PyInstaller to create standalone executable

# install.bat
@echo off
REM Download Python embeddable package
REM https://www.python.org/ftp/python/3.11.6/python-3.11.6-embed-amd64.zip

REM Download LilyPond for Windows
REM http://lilypond.org/windows.html

REM Install dependencies
python.exe -m pip install abjad music21 python-ly

REM Create launcher
echo @echo off > codempose.bat
echo set PATH=%~dp0python;%~dp0lilypond\bin;%%PATH%% >> codempose.bat
echo set PYTHONPATH=%~dp0src >> codempose.bat
echo python.exe %%* >> codempose.bat

REM Package with NSIS or Inno Setup for installer
```

---

## 📦 OPTION 4: Python Wheel + Instructions (Minimal)

### Create Python Package

```bash
# Create setup.py
cat > setup.py << 'EOF'
from setuptools import setup, find_packages

setup(
    name="codempose",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "abjad>=3.19",
        "music21>=9.1.0",
        "python-ly>=0.9.7",
    ],
    python_requires=">=3.11",
    entry_points={
        "console_scripts": [
            "codempose-generate=generate_study:main",
        ],
    },
    include_package_data=True,
)
EOF

# Build wheel
python -m pip install build
python -m build

# Distribution size: ~50 MB (just Python code)
# dist/codempose-1.0.0-py3-none-any.whl
```

### User Installation

```bash
# Install Python 3.11+
# Install LilyPond separately

# Install Codempose
pip install codempose-1.0.0-py3-none-any.whl

# Use
codempose-generate 1 "My Study"
python my_study.py
```

---

## 🎯 RECOMMENDED DISTRIBUTION STRATEGY

### For End Users (Composers)
**→ Use Docker Container (Option 1)**
- Single download, works everywhere
- No configuration needed
- Includes everything

### For Researchers/Academics
**→ Use Conda Environment (Option 2)**
- Familiar to scientific community
- Easy dependency management
- Reproducible research

### For Power Users
**→ Use Python Wheel (Option 4) + Installation Guide**
- Minimal size
- Integrates with existing workflow
- Most flexible

### For Distribution Platforms
**→ Create Platform-Specific Bundles (Option 3)**
- Linux: AppImage or .tar.gz
- macOS: .dmg with .app bundle
- Windows: .exe installer with embedded Python

---

## 📋 COMPLETE DISTRIBUTION CHECKLIST

### Files to Include

```
codempose-release/
├── README.md                      ← Quick start guide
├── DISTRIBUTION_GUIDE.md          ← This file
├── LICENSE                        ← Your license
├── requirements.txt               ← Python dependencies
├── environment.yml                ← Conda environment
├── Dockerfile                     ← Docker build
├── generate_study.py              ← User script
├── CODEMPOSE_STUDY_TEMPLATES.py   ← Templates
├── src/                           ← All core code
├── studies/                       ← Examples
│   ├── README.md
│   └── OLD/                       ← Example studies
├── outputs/                       ← Example outputs
│   ├── TEMPLATES/                 ← Reference materials
│   └── DOCUMENTATION/             ← Full documentation
└── tests/                         ← Test suite
```

### System Requirements Documentation

```markdown
## System Requirements

### Minimum Requirements
- **CPU**: 64-bit processor (x86_64 or ARM64)
- **RAM**: 2 GB minimum, 4 GB recommended
- **Disk**: 1 GB free space
- **OS**: Linux, macOS 10.15+, Windows 10+

### Software Dependencies
- **Python**: 3.11 or later
- **LilyPond**: 2.24.3 or later

### Optional
- **Docker**: For container-based distribution
- **Conda/Miniconda**: For Conda distribution
- **MuseScore**: For viewing/editing MusicXML files
```

---

## 🚀 QUICK START SCRIPTS

### Linux/macOS One-Liner

```bash
# Docker-based (recommended)
curl -L https://example.com/codempose-docker.tar.gz | docker load && \
docker run -it -v $(pwd)/studies:/codempose/studies codempose:latest

# Or traditional install
curl -L https://example.com/codempose-latest.tar.gz | tar xz && \
cd codempose && \
./install.sh && \
source venv/bin/activate && \
python generate_study.py 1 "My First Study"
```

### Windows PowerShell

```powershell
# Download and extract
Invoke-WebRequest -Uri "https://example.com/codempose-win64.zip" -OutFile "codempose.zip"
Expand-Archive -Path "codempose.zip" -DestinationPath "."
cd codempose

# Run
.\codempose.bat generate_study.py 1 "My First Study"
```

---

## 📊 DISTRIBUTION SIZE COMPARISON

| Method | Compressed | Extracted | Dependencies Included |
|--------|-----------|-----------|----------------------|
| Docker Image | 1.5-2 GB | 3-4 GB | ✅ Everything |
| Conda Pack | 1-2 GB | 2-3 GB | ✅ Everything |
| Linux Bundle | 500-800 MB | 1-1.5 GB | ✅ Python + LilyPond |
| macOS .dmg | 600-900 MB | 1.2-1.8 GB | ✅ Python + LilyPond |
| Windows Installer | 500-800 MB | 1-1.5 GB | ✅ Python + LilyPond |
| Python Wheel | 50 MB | 100 MB | ❌ User installs |
| Codempose Only | 19 MB | 50 MB | ❌ User installs all |

---

## 🎵 RECOMMENDED APPROACH

**For your use case, I recommend**:

### Primary Distribution: Docker Container
```bash
# Build once
docker build -t codempose:1.0 .
docker save codempose:1.0 | gzip > codempose-docker-1.0.tar.gz

# Users load and run
docker load < codempose-docker-1.0.tar.gz
docker run -it -v $(pwd):/work codempose:1.0
```

**Advantages**:
- ✅ Works on any platform with Docker
- ✅ Includes Python, LilyPond, all dependencies
- ✅ Reproducible environment
- ✅ Easy to update (rebuild image)
- ✅ ~1.5 GB - acceptable for modern networks

### Secondary: Codempose Tarball + Instructions
- Provide `codempose-release-YYYYMMDD.tar.gz` (19 MB)
- Include `INSTALLATION.md` with Python + LilyPond setup
- For users with existing environments

---

## ✅ NEXT STEPS

1. **Choose distribution method** based on target audience
2. **Create Dockerfile** (if using Docker)
3. **Write installation guide** specific to chosen method
4. **Test on clean system** to verify it works
5. **Create download page** or repository release
6. **Document system requirements** clearly

Would you like me to create any of these distribution packages for you?
