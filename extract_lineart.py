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

def extract_lineart(input_path, output_path, model_dir=None, coarse=False, threshold=127, apply_morphology=True):
    """
    Extract lineart from an image using LineAnimeDetector
    
    Args:
        input_path: Path to input image
        output_path: Path to save lineart
        model_dir: Path to model directory (default: ./models)
        coarse: Use coarse model (sk_model2.pth) vs fine model (sk_model.pth)
        threshold: Threshold for binary conversion (0-255)
        apply_morphology: Apply morphological opening to remove noise
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
    
    # Extract lineart (no resize needed - works with any size)
    lineart = detector(image, coarse=coarse)
    
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
    
    # Save result
    cv2.imwrite(output_path, cleaned_lineart)
    print(f"Binary lineart saved to: {output_path}")

def main():
    parser = argparse.ArgumentParser(
        description="Extract lineart from images using MangaNinjia's LineAnimeDetector",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python extract_lineart.py input.jpg output.png
    python extract_lineart.py input.jpg output.png --coarse --threshold 100
    python extract_lineart.py input.jpg output.png --no-morphology
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
    
    args = parser.parse_args()
    
    try:
        extract_lineart(
            args.input, 
            args.output, 
            args.model_dir,
            args.coarse, 
            args.threshold,
            not args.no_morphology
        )
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()