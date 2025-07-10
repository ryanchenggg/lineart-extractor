#!/usr/bin/env python3
"""
Download MangaNinjia lineart detection models
Models are downloaded from HuggingFace Hub for better availability
"""

import os
import sys
import argparse
from urllib.request import urlretrieve
from urllib.error import URLError
import hashlib

# Model information
MODELS = {
    'sk_model.pth': {
        'url': 'https://huggingface.co/lllyasviel/Annotators/resolve/main/sk_model.pth',
        'size': '44.7 MB',
        'description': 'Fine lineart detection model (recommended)'
    },
    'sk_model2.pth': {
        'url': 'https://huggingface.co/lllyasviel/Annotators/resolve/main/sk_model2.pth', 
        'size': '44.7 MB',
        'description': 'Coarse lineart detection model (faster)'
    }
}

def download_with_progress(url, filepath):
    """Download file with progress bar"""
    def progress_hook(block_num, block_size, total_size):
        if total_size > 0:
            percent = min(100, (block_num * block_size * 100) // total_size)
            sys.stdout.write(f'\rDownloading: {percent}% ')
            sys.stdout.flush()
    
    try:
        urlretrieve(url, filepath, progress_hook)
        print(' ✓')
        return True
    except URLError as e:
        print(f' ✗ Failed: {e}')
        return False

def check_model_exists(model_path):
    """Check if model file exists and has reasonable size"""
    if os.path.exists(model_path):
        size = os.path.getsize(model_path)
        return size > 1024 * 1024  # At least 1MB
    return False

def download_models(model_dir, models_to_download=None):
    """Download specified models to model directory"""
    # Create model directory
    os.makedirs(model_dir, exist_ok=True)
    
    if models_to_download is None:
        models_to_download = list(MODELS.keys())
    
    print(f"Downloading models to: {model_dir}")
    print("-" * 50)
    
    success_count = 0
    for model_name in models_to_download:
        if model_name not in MODELS:
            print(f"Unknown model: {model_name}")
            continue
        
        model_info = MODELS[model_name]
        model_path = os.path.join(model_dir, model_name)
        
        # Check if already exists
        if check_model_exists(model_path):
            print(f"✓ {model_name} already exists ({model_info['size']})")
            success_count += 1
            continue
        
        print(f"Downloading {model_name} ({model_info['size']})...")
        print(f"  {model_info['description']}")
        
        if download_with_progress(model_info['url'], model_path):
            if check_model_exists(model_path):
                success_count += 1
            else:
                print(f"  Warning: Downloaded file seems too small")
        else:
            # Clean up failed download
            if os.path.exists(model_path):
                os.remove(model_path)
    
    print("-" * 50)
    print(f"Successfully downloaded {success_count}/{len(models_to_download)} models")
    
    if success_count == 0:
        print("No models were downloaded successfully!")
        return False
    
    return True

def main():
    parser = argparse.ArgumentParser(description="Download MangaNinjia lineart detection models")
    parser.add_argument("--model-dir", default=".", 
                       help="Directory to download models (default: current directory)")
    parser.add_argument("--fine-only", action="store_true",
                       help="Download only fine model (sk_model.pth)")
    parser.add_argument("--coarse-only", action="store_true", 
                       help="Download only coarse model (sk_model2.pth)")
    parser.add_argument("--list", action="store_true",
                       help="List available models")
    
    args = parser.parse_args()
    
    if args.list:
        print("Available models:")
        for name, info in MODELS.items():
            print(f"  {name}: {info['description']} ({info['size']})")
        return
    
    # Determine which models to download
    if args.fine_only:
        models_to_download = ['sk_model.pth']
    elif args.coarse_only:
        models_to_download = ['sk_model2.pth']
    else:
        models_to_download = list(MODELS.keys())
    
    success = download_models(args.model_dir, models_to_download)
    
    if success:
        print("\nModels ready! You can now use extract_lineart.py")
    else:
        print("\nDownload failed. Please check your internet connection and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()