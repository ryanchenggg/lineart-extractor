#!/usr/bin/env python3
"""
Extract raw lineart without any post-processing
Based on extract_lineart.py but removes binarization and morphological operations
"""

import os
import sys
import numpy as np
import torch
from PIL import Image
import cv2

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from annotator.lineart import LineartDetector

def extract_raw_lineart(input_path, output_path):
    # Initialize detector
    model_dir = os.path.join(os.path.dirname(__file__), 'models')
    detector = LineartDetector(model_dir)
    
    # Load image
    image = cv2.imread(input_path)
    if image is None:
        raise ValueError(f"Could not load image: {input_path}")
    
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    print(f'Processing image: {input_path} ({image.shape[1]}x{image.shape[0]})')
    
    # Extract raw lineart (no post-processing)
    lineart = detector(image, coarse=False)
    
    # Resize to match original if needed
    original_height, original_width = image.shape[:2]
    if lineart.shape != (original_height, original_width):
        print(f'Size mismatch: {original_width}x{original_height} -> {lineart.shape[1]}x{lineart.shape[0]}')
        print('Resizing to match original dimensions...')
        lineart = cv2.resize(lineart, (original_width, original_height), interpolation=cv2.INTER_LANCZOS4)
    
    # Save raw output (no binarization, no morphology)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cv2.imwrite(output_path, lineart)
    print(f'Raw lineart saved to: {output_path}')

if __name__ == "__main__":
    input_path = "/home/ryan/Colorization/lineart-extractor/examples/input/ai01_187_Simple_L-C_F-51_G.png"
    output_path = "examples/output/raw_lineart.png"
    extract_raw_lineart(input_path, output_path)