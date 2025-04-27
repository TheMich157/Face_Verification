# Installation Guide

## Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- git (optional, for cloning repository)

## Quick Installation (Windows)
```bash
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate

# Install required packages
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

## Quick Installation (Linux/Mac)
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install required packages
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

## Detailed Installation Steps

### 1. System Requirements

#### Windows:
```bash
# Install Visual Studio Build Tools (if needed)
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
# Select: Desktop development with C++
```

#### Linux (Ubuntu/Debian):
```bash
# Install required system packages
sudo apt-get update
sudo apt-get install -y python3-dev python3-pip
sudo apt-get install -y cmake build-essential pkg-config
sudo apt-get install -y libx11-dev libatlas-base-dev
sudo apt-get install -y libgtk-3-dev libboost-python-dev
```

#### macOS:
```bash
# Install Homebrew if needed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install required packages
brew install cmake pkg-config
brew install python3
```

### 2. Virtual Environment Setup
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

### 3. Install Dependencies

#### Step 1: Core Dependencies
```bash
# Install basic requirements
pip install discord.py python-dotenv SQLAlchemy
```

#### Step 2: Image Processing
```bash
# Install OpenCV and NumPy
pip install opencv-python numpy

# Install face-recognition
pip install face-recognition
```

#### Step 3: Other Dependencies
```bash
# Install remaining packages
pip install -r requirements.txt
```

## Troubleshooting

### Common Issues

#### 1. face-recognition Installation Fails
```bash
# Windows:
pip install cmake
pip install face-recognition

# Linux:
sudo apt-get install cmake
pip install face-recognition

# Mac:
brew install cmake
pip install face-recognition
```

#### 2. OpenCV Issues
```bash
# Try alternative installation
pip uninstall opencv-python
pip install opencv-python-headless
```

#### 3. NumPy Issues
```bash
# Install specific version
pip install numpy==1.24.3
```

#### 4. Discord.py Issues
```bash
# Reinstall discord.py
pip uninstall discord.py
pip install discord.py==2.3.2
```

### Verification Steps

1. Test Python Installation:
```bash
python --version  # Should be 3.8 or higher
```

2. Test Package Installation:
```python
# Run Python and try imports
import discord
import face_recognition
import cv2
import numpy
```

3. Test Bot Connection:
```bash
# Run the bot
python src/bot.py
```

## Post-Installation Setup

1. Configure Bot Token:
   - Open `config/config.json`
   - Add your Discord bot token

2. Test Face Detection:
```python
from src.utils.face_detection import FaceDetector
detector = FaceDetector()
# Should initialize without errors
```

3. Verify Database:
   - Bot will create database automatically
   - Check for `verification_data.db` file

## Updating

To update existing installation:
```bash
# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Update packages
pip install --upgrade -r requirements.txt
```

## Security Notes

- Keep virtual environment active when running bot
- Don't share your bot token
- Regular updates recommended
- Monitor system resources

## Support

If you encounter issues:
1. Check error messages
2. Verify Python version
3. Confirm all dependencies installed
4. Review system requirements
5. Check installation logs

For additional help:
- Review error logs
- Check Discord API status
- Verify system compatibility
- Contact support team

Remember to keep your bot token secure and never share it publicly!
