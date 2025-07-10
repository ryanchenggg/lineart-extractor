# Lineart Extractor

A standalone tool for extracting clean lineart from images using MangaNinjia's LineAnimeDetector. Works with any image size without resolution constraints.

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
# Basic usage
python extract_lineart.py input.jpg output.png

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
    apply_morphology=True   # Remove noise
)
```

## Examples

| Input | Output |
|-------|--------|
| ![Input](examples/input/sample.jpg) | ![Output](examples/output/sample_lineart.png) |

## Models

Two pre-trained models are available:

- **sk_model.pth** (44.7 MB): Fine model for high-quality results
- **sk_model2.pth** (44.7 MB): Coarse model for faster processing

Models are automatically downloaded from [HuggingFace Hub](https://huggingface.co/lllyasviel/Annotators).

## Parameters

### Threshold
- **Range**: 0-255
- **Default**: 127
- **Lower values**: Capture more edges (may include noise)
- **Higher values**: More selective (may miss faint edges)

### Morphological Filtering
- **Default**: Enabled
- **Purpose**: Removes small noise spots while preserving line structure
- **Disable**: Use `--no-morphology` for raw model output

## Requirements

- Python 3.8+
- PyTorch 1.9+
- CUDA-capable GPU (recommended)
- 2GB+ free disk space for models

## Performance

| Resolution | Fine Model | Coarse Model |
|------------|------------|--------------|
| 512x512    | ~0.5s      | ~0.3s        |
| 1024x1024  | ~1.2s      | ~0.8s        |
| 2048x2048  | ~3.5s      | ~2.1s        |

*Times measured on RTX 3080*

## Troubleshooting

### Model Download Issues
```bash
# Check internet connection and retry
python models/download_models.py

# Download to specific directory
python models/download_models.py --model-dir /path/to/models
```

### CUDA Out of Memory
```bash
# Use coarse model for lower memory usage
python extract_lineart.py input.jpg output.png --coarse
```

### Poor Results
```bash
# Adjust threshold for your image type
python extract_lineart.py input.jpg output.png --threshold 100

# Try coarse model for different style
python extract_lineart.py input.jpg output.png --coarse
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Original Work**: [MangaNinjia](https://github.com/originalauthor/manganinjia)
- **Lineart Detection**: [Informative Drawings](https://github.com/carolineec/informative-drawings)
- **ControlNet**: [Adding Conditional Control to Text-to-Image Diffusion Models](https://arxiv.org/abs/2302.05543)
- **Models**: [lllyasviel/Annotators](https://huggingface.co/lllyasviel/Annotators)

## Citation

If you use this tool in your research, please cite:

```bibtex
@misc{lineart-extractor,
  title={Lineart Extractor: Standalone Tool for AI-Powered Line Art Extraction},
  author={Your Name},
  year={2024},
  url={https://github.com/yourusername/lineart-extractor}
}
```
