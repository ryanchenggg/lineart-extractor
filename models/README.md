# Models

This directory contains the pre-trained models for lineart detection.

## Download Models

Run the download script to get the required models:

```bash
python download_models.py
```

## Available Models

- **sk_model.pth** (44.7 MB): Fine lineart detection model (recommended)
  - High quality results
  - Better for detailed artwork
  - Default model used

- **sk_model2.pth** (44.7 MB): Coarse lineart detection model  
  - Faster processing
  - Good for simple line drawings
  - Use with `--coarse` flag

## Download Options

```bash
# Download all models
python download_models.py

# Download only fine model
python download_models.py --fine-only

# Download only coarse model  
python download_models.py --coarse-only

# Download to specific directory
python download_models.py --model-dir /path/to/models

# List available models
python download_models.py --list
```

## Model Sources

Models are downloaded from:
- **Original Source**: [ControlNet Annotators](https://huggingface.co/lllyasviel/Annotators)
- **Paper**: [Adding Conditional Control to Text-to-Image Diffusion Models](https://arxiv.org/abs/2302.05543)
- **Based on**: [Informative Drawings](https://github.com/carolineec/informative-drawings)

## License

Models follow the original licensing terms from their respective sources.