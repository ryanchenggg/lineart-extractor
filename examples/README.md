# Examples

This directory contains example input and output images.

## Directory Structure

- `input/`: Example input images
- `output/`: Generated lineart outputs

## Running Examples

```bash
# Process example image
python extract_lineart.py examples/input/sample.jpg examples/output/sample_lineart.png

# Try different settings
python extract_lineart.py examples/input/sample.jpg examples/output/sample_coarse.png --coarse
python extract_lineart.py examples/input/sample.jpg examples/output/sample_thresh80.png --threshold 80
```

## Adding Your Examples

1. Place input images in `examples/input/`
2. Run the extractor to generate outputs in `examples/output/`
3. Consider different parameter combinations to show versatility

## Sample Results

| Setting | Command | Description |
|---------|---------|-------------|
| Default | `python extract_lineart.py input.jpg output.png` | Standard quality |
| Coarse | `python extract_lineart.py input.jpg output.png --coarse` | Faster processing |
| Low Threshold | `python extract_lineart.py input.jpg output.png --threshold 80` | More edges |
| High Threshold | `python extract_lineart.py input.jpg output.png --threshold 160` | Cleaner lines |