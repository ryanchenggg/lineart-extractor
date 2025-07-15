#!/usr/bin/env python3
"""
Standalone lineart extraction using MangaNinjia's LineAnimeDetector
Supports any image size without (512, 512) constraint

Repository: https://github.com/yourusername/lineart-extractor
Original: Based on MangaNinjia project
"""

import os
import sys
import argparse
import numpy as np
import torch
from PIL import Image
import cv2

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from annotator.lineart import LineartDetector

def extract_lineart(input_path, output_path, model_dir=None, coarse=False, threshold=127, apply_morphology=True, output_format='binary'):
    """
    Extract lineart from an image using LineAnimeDetector
    
    Args:
        input_path: Path to input image
        output_path: Path to save lineart
        model_dir: Path to model directory (default: ./models)
        coarse: Use coarse model (sk_model2.pth) vs fine model (sk_model.pth)
        threshold: Threshold for binary conversion (0-255)
        apply_morphology: Apply morphological opening to remove noise
        output_format: Output format ('binary', 'rgb', 'rgba')
    """
    # Default model directory
    if model_dir is None:
        model_dir = os.path.join(os.path.dirname(__file__), 'models')
    
    # Check if models exist
    fine_model = os.path.join(model_dir, 'sk_model.pth')
    coarse_model = os.path.join(model_dir, 'sk_model2.pth')
    
    if not os.path.exists(fine_model):
        raise FileNotFoundError(f"Model not found: {fine_model}\nRun: python models/download_models.py")
    
    if coarse and not os.path.exists(coarse_model):
        raise FileNotFoundError(f"Coarse model not found: {coarse_model}\nRun: python models/download_models.py")
    
    # Initialize detector
    detector = LineartDetector(model_dir)
    
    # Load and preprocess image
    image = cv2.imread(input_path)
    if image is None:
        raise ValueError(f"Could not load image: {input_path}")
    
    # Convert BGR to RGB
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    print(f"Processing image: {input_path} ({image.shape[1]}x{image.shape[0]})")
    
    # Store original dimensions
    original_height, original_width = image.shape[:2]
    
    # Extract lineart (no resize needed - works with any size)
    lineart = detector(image, coarse=coarse)
    
    # Check if output size matches input size
    if lineart.shape != (original_height, original_width):
        print(f"Size mismatch detected: {original_width}x{original_height} -> {lineart.shape[1]}x{lineart.shape[0]}")
        print(f"Resizing lineart to match original dimensions...")
        lineart = cv2.resize(lineart, (original_width, original_height), interpolation=cv2.INTER_LANCZOS4)
    
    # Convert to binary image to filter noise
    _, binary_lineart = cv2.threshold(lineart, threshold, 255, cv2.THRESH_BINARY)
    
    # Apply morphological opening to remove noise (optional)
    if apply_morphology:
        kernel = np.ones((3, 3), np.uint8)
        cleaned_lineart = cv2.morphologyEx(binary_lineart, cv2.MORPH_OPEN, kernel)
    else:
        cleaned_lineart = binary_lineart
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Convert to desired output format
    if output_format.lower() == 'binary':
        final_output = cleaned_lineart
        print(f"Binary lineart saved to: {output_path}")
    elif output_format.lower() == 'rgb':
        # Convert single channel to RGB (3 channels)
        final_output = cv2.cvtColor(cleaned_lineart, cv2.COLOR_GRAY2RGB)
        print(f"RGB lineart saved to: {output_path}")
    elif output_format.lower() == 'rgba':
        # Convert single channel to RGBA (4 channels)
        # Create alpha channel: white becomes transparent, black stays opaque
        alpha_channel = 255 - cleaned_lineart  # Invert: black lines = opaque (255), white bg = transparent (0)
        rgb_lineart = cv2.cvtColor(cleaned_lineart, cv2.COLOR_GRAY2RGB)
        final_output = cv2.merge([rgb_lineart[:,:,0], rgb_lineart[:,:,1], rgb_lineart[:,:,2], alpha_channel])
        print(f"RGBA lineart saved to: {output_path}")
    else:
        raise ValueError(f"Unsupported output format: {output_format}. Use 'binary', 'rgb', or 'rgba'")
    
    # Save result
    if output_format.lower() == 'rgba':
        # Use PIL for RGBA PNG saving
        pil_image = Image.fromarray(final_output, 'RGBA')
        pil_image.save(output_path)
    else:
        cv2.imwrite(output_path, final_output)

def main():
    parser = argparse.ArgumentParser(
        description="Extract lineart from images using MangaNinjia's LineAnimeDetector",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python extract_lineart.py input.jpg output.png
    python extract_lineart.py input.jpg output.png --coarse --threshold 100
    python extract_lineart.py input.jpg output.png --no-morphology
    python extract_lineart.py input.jpg output.png --format rgb
    python extract_lineart.py input.jpg output.png --format rgba
        """
    )
    parser.add_argument("input", help="Input image path")
    parser.add_argument("output", help="Output lineart path")
    parser.add_argument("--model-dir", default=None,
                       help="Path to model directory (default: ./models)")
    parser.add_argument("--coarse", action="store_true", 
                       help="Use coarse model (sk_model2.pth) for faster processing")
    parser.add_argument("--threshold", type=int, default=127,
                       help="Threshold for binary conversion (0-255, default: 127)")
    parser.add_argument("--no-morphology", action="store_true",
                       help="Skip morphological noise removal")
    parser.add_argument("--format", choices=['binary', 'rgb', 'rgba'], default='binary',
                       help="Output format: binary (grayscale), rgb (3-channel), rgba (4-channel with transparency)")
    
    args = parser.parse_args()
    
    try:
        extract_lineart(
            args.input, 
            args.output, 
            args.model_dir,
            args.coarse, 
            args.threshold,
            not args.no_morphology,
            args.format
        )
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()