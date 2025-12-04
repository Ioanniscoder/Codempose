# Codempose - Complete Distribution Setup

## Installation Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Quick Start

1. **Extract the tarball:**
   ```bash
   tar -xzf codempose_complete_distribution.tar.gz
   cd codempose_complete_distribution
   ```

2. **Configure paths (IMPORTANT on Windows):**
   ```bash
   python setup_paths.py
   ```
   This ensures all path configurations are set correctly, especially if `_study_path.py` wasn't extracted.

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run a study example:**
   ```bash
   python generate_study.py
   ```

### What's Included

- **src/** - Core library modules:
  - `project_template.py` - Main composition template engine
  - `lilypond_parser.py` - LilyPond notation parser
  - `lily_tokenizer.py` - Tokenizer for LilyPond syntax
  - `lily_token_parser.py` - Token parser
  - `lily_to_tiny.py` - Converter to TinyNotation
  - `score_builder.py` - Score construction utilities
  - `transformations.py` - Musical transformations
  - `harmonic_engine.py` - Harmonic analysis engine
  - And more...

- **studies/** - Example compositions and study files
  - `100th.py` - Latest feature demonstration
  - `generate_study.py` - Study template generator
  - Various example studies

- **generate_study.py** - Quick study generator script

### Platform Compatibility

This distribution includes proper UTF-8 encoding for all file operations, ensuring compatibility across:
- ✅ Windows (including cp1252 systems)
- ✅ Linux
- ✅ macOS

### Documentation

- `README.md` - Project overview
- `BARLINE_VALIDATION_SUMMARY.md` - Barline handling documentation
- `studies/README.md` - Guide to study examples

### Troubleshooting

**Missing `_study_path.py` on Windows:**
If study files can't import modules, run the setup script:
```bash
python setup_paths.py
```
This recreates the path configuration file if it was skipped during extraction.

**Windows Users:** If you encounter encoding errors, ensure your terminal is set to UTF-8:
```cmd
chcp 65001
```

**Python Version:** Verify you're using Python 3.8+:
```bash
python --version
```

### Support

For issues or questions, refer to the README.md file or check the documentation in the studies directory.
