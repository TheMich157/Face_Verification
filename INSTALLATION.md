# Installation Guide

## Quick Start (5 minutes)

### Windows
```bash
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### Linux/Mac
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

## System Requirements

- Python 3.8-3.11 (3.12 not yet fully supported by all dependencies)
- 4GB RAM minimum
- Webcam (optional, for video verification)

## Detailed Installation Steps

### 1. Python Setup

#### Windows
1. Download Python from [python.org](https://www.python.org/downloads/)
2. Choose Python 3.11 for best compatibility
3. Check "Add Python to PATH" during installation

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
```

#### macOS
```bash
brew install python@3.11
```

### 2. Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Upgrade basic tools
pip install --upgrade pip setuptools wheel
```

### 3. Dependencies Installation

```bash
# Install core requirements
pip install discord.py python-dotenv

# Install MediaPipe (face detection)
pip install mediapipe

# Install remaining packages
pip install -r requirements.txt
```

## Common Issues & Solutions

### 1. Installation Errors

#### "ERROR: Could not build wheels for numpy"
```bash
# Solution 1: Install numpy separately first
pip install numpy==1.24.3

# Solution 2: Use pre-built wheel
pip install numpy --only-binary :all:
```

#### MediaPipe Installation Issues
```bash
# Solution 1: Install specific version
pip install mediapipe==0.10.8

# Solution 2: Install dependencies first
pip install numpy opencv-python-headless
pip install mediapipe
```

#### OpenCV Issues
```bash
# If opencv-python-headless fails:
pip uninstall opencv-python-headless
pip install opencv-python
```

### 2. Runtime Errors

#### Import Errors
```bash
# Verify installation
pip list

# Reinstall problematic package
pip uninstall package_name
pip install package_name
```

#### Face Detection Issues
```bash
# Check MediaPipe installation
python -c "import mediapipe as mp; print(mp.__version__)"

# Reinstall if needed
pip uninstall mediapipe
pip install mediapipe==0.10.8
```

## Verification Steps

1. Test Dependencies:
```python
# Run Python and test imports
import discord
import mediapipe
import cv2
import numpy
```

2. Test Face Detection:
```python
from src.utils.face_detection import FaceDetector
detector = FaceDetector()
# Should initialize without errors
```

3. Test Bot:
```bash
python src/bot.py
```

## Configuration

1. Discord Bot Token:
   - Open `config/config.json`
   - Add your bot token:
     ```json
     {
         "bot_token": "YOUR_TOKEN_HERE"
     }
     ```

2. Verify Permissions:
   - Bot needs administrator permissions
   - Or specific permissions:
     - Manage Roles
     - Manage Messages
     - Send Messages
     - etc.

## Updating

```bash
# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Update packages
pip install --upgrade -r requirements.txt
```

## Troubleshooting Tips

1. Version Conflicts:
   ```bash
   pip freeze > current_requirements.txt
   pip uninstall -r current_requirements.txt -y
   pip install -r requirements.txt
   ```

2. Clean Installation:
   ```bash
   deactivate
   rm -rf venv
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Debug Mode:
   ```bash
   # Enable debug logging
   python -m pip install --verbose -r requirements.txt
   ```

## Support

If you encounter issues:
1. Check error messages
2. Verify Python version
3. Review dependencies
4. Check system requirements
5. Consult documentation

For additional help:
- Review error logs
- Check Discord API status
- Verify system compatibility
- Contact support team

Remember: Keep your bot token secure and never share it publicly!
