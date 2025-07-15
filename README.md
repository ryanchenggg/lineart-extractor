# Lineart Extractor

A standalone tool for extracting clean lineart from images using LineAnimeDetector from ControlNet. Works with any image size without resolution constraints.

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

## Usage

### Command Line Interface

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

### Python API

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
## Models

Two pre-trained models are available:

- **sk_model.pth** (44.7 MB): Fine model for high-quality results
- **sk_model2.pth** (44.7 MB): Coarse model for faster processing

Models are automatically downloaded from [HuggingFace Hub](https://huggingface.co/lllyasviel/Annotators).

## Output Formats

The tool supports three output formats:

- **binary** (default): Single-channel grayscale image with white background and black lines
- **rgb**: 3-channel RGB image with white background and black lines  
- **rgba**: 4-channel RGBA image with transparent background and black lines

### Format Examples

```bash
# Binary output (traditional)
python extract_lineart.py anime.jpg lineart_binary.png --format binary

# RGB output (for compatibility with RGB workflows)
python extract_lineart.py anime.jpg lineart_rgb.png --format rgb

# RGBA output (transparent background for overlays)
python extract_lineart.py anime.jpg lineart_rgba.png --format rgba
```

## TODO

- [ ] **Enhanced Morphology Configuration**: Allow users to specify different morphological operations and kernel sizes for noise removal (currently limited to 3x3 opening operation)
- [ ] **Morphology Strategy Testing**: Implement and evaluate different noise removal strategies (erosion, dilation, opening, closing, gradient operations) with various kernel sizes to determine optimal configurations for different image types
