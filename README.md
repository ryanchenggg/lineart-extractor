# Lineart Extractor

A standalone tool for extracting clean lineart from images with two methods:
1. **AI-based extraction** using LineAnimeDetector from ControlNet for general images
2. **Simple pixel-based extraction** for datasets with specific line art colors (e.g., RGB(10,10,10))

Works with any image size without resolution constraints.

## Installation

### Method 1: Conda (Recommended)

```bash
# Clone repository
git clone https://github.com/yourusername/lineart-extractor.git
cd lineart-extractor

# Create conda environment
conda env create -f environment.yml
conda activate lineart-extractor

# Download models
python models/download_models.py
```

### Method 2: pip

```bash
# Clone repository
git clone https://github.com/yourusername/lineart-extractor.git
cd lineart-extractor

# Install dependencies
pip install -r requirements.txt

# Download models
python models/download_models.py
```

## Quick Start

### Interactive Mode (Recommended)

```bash
# Run the interactive script to choose extraction method
./run_extract.sh input.jpg output.png

# The script will prompt you to choose:
# 1. AI-based extraction (extract_lineart.py)
# 2. Simple pixel-based extraction (extract_simple_lineart.py)
# 3. Extract frames (extract_frames.py)
```

### Direct Usage

#### AI-based Extraction
```bash
# Basic usage (binary/grayscale output)
python extract_lineart.py input.jpg output.png

# RGB format output (3-channel)
python extract_lineart.py input.jpg output.png --format rgb

# RGBA format output (4-channel with transparency)
python extract_lineart.py input.jpg output.png --format rgba

# With custom threshold
python extract_lineart.py input.jpg output.png --threshold 100

# Use coarse model for faster processing
python extract_lineart.py input.jpg output.png --coarse

# Skip noise removal for raw output
python extract_lineart.py input.jpg output.png --no-morphology
```

#### Simple Pixel-based Extraction
```bash
# Basic usage (for RGB(10,10,10) line art)
python extract_simple_lineart.py input.jpg output.png

# Custom line color
python extract_simple_lineart.py input.jpg output.png --line-color 10 10 10

# Custom background color
python extract_simple_lineart.py input.jpg output.png --bg-color 255 255 255
```

## Usage

### Interactive Script

```bash
./run_extract.sh [input] [output] [options]

# The script will prompt you to choose between:
# 1. AI-based extraction (extract_lineart.py)
# 2. Simple pixel-based extraction (extract_simple_lineart.py)
# 3. Extract frames (extract_frames.py)
```

### AI-based Extraction (extract_lineart.py)

```bash
python extract_lineart.py [input] [output] [options]

Arguments:
  input                 Input image path
  output               Output lineart path

Options:
  --model-dir DIR      Path to model directory (default: ./models)
  --coarse            Use coarse model for faster processing
  --threshold INT     Binary threshold 0-255 (default: 127)
  --no-morphology     Skip morphological noise removal
  --format FORMAT     Output format: binary, rgb, rgba (default: binary)
  -h, --help          Show help message
```

### Simple Pixel-based Extraction (extract_simple_lineart.py)

```bash
python extract_simple_lineart.py [input] [output] [options]

Arguments:
  input                 Input image path
  output               Output lineart path

Options:
  --line-color R G B   RGB color of line art (default: 10 10 10)
  --bg-color R G B     RGB color for background (default: 255 255 255)
  -h, --help          Show help message
```

### Python API

#### AI-based Extraction
```python
from extract_lineart import extract_lineart

# Basic usage
extract_lineart('input.jpg', 'output.png')

# With custom parameters
extract_lineart(
    input_path='input.jpg',
    output_path='output.png',
    coarse=False,           # Use fine model
    threshold=127,          # Binary threshold
    apply_morphology=True,  # Remove noise
    output_format='binary'  # Output format: 'binary', 'rgb', 'rgba'
)
```

#### Simple Pixel-based Extraction
```python
from extract_simple_lineart import extract_simple_lineart

# Basic usage
extract_simple_lineart('input.jpg', 'output.png')

# With custom parameters
extract_simple_lineart(
    input_path='input.jpg',
    output_path='output.png',
    line_color=(10, 10, 10),    # RGB color of line art
    bg_color=(255, 255, 255)    # RGB color for background
)
```
## Extraction Methods

### AI-based Extraction
Uses LineAnimeDetector from ControlNet for general-purpose line art extraction from any image.

**Models required:**
- **sk_model.pth** (44.7 MB): Fine model for high-quality results
- **sk_model2.pth** (44.7 MB): Coarse model for faster processing

Models are automatically downloaded from [HuggingFace Hub](https://huggingface.co/lllyasviel/Annotators).

### Simple Pixel-based Extraction
No AI models required. Perfect for datasets where line art has a specific color (e.g., RGB(10,10,10)). Simply converts non-line pixels to white background.

**Use cases:**
- Datasets with consistent line art colors
- Pre-processed images with specific color schemes
- Fast processing without AI computation
- When you need exact pixel-level control

## Output Formats

### AI-based Extraction
Supports three output formats:

- **binary** (default): Single-channel grayscale image with white background and black lines
- **rgb**: 3-channel RGB image with white background and black lines  
- **rgba**: 4-channel RGBA image with transparent background and black lines

```bash
# Binary output (traditional)
python extract_lineart.py anime.jpg lineart_binary.png --format binary

# RGB output (for compatibility with RGB workflows)
python extract_lineart.py anime.jpg lineart_rgb.png --format rgb

# RGBA output (transparent background for overlays)
python extract_lineart.py anime.jpg lineart_rgba.png --format rgba
```

### Simple Pixel-based Extraction
Outputs RGB format with customizable colors:

```bash
# Default: RGB(10,10,10) lines on RGB(255,255,255) background
python extract_simple_lineart.py input.jpg output.png

# Custom colors
python extract_simple_lineart.py input.jpg output.png --line-color 0 0 0 --bg-color 255 255 255
```

## TODO

- [ ] **Enhanced Morphology Configuration**: Allow users to specify different morphological operations and kernel sizes for noise removal (currently limited to 3x3 opening operation)
- [ ] **Morphology Strategy Testing**: Implement and evaluate different noise removal strategies (erosion, dilation, opening, closing, gradient operations) with various kernel sizes to determine optimal configurations for different image types
