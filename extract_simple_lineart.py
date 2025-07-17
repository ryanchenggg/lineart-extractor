#!/usr/bin/env python3
"""
Simple lineart extraction for datasets with RGB(10,10,10) line art.
Converts all non-lineart pixels to white (255,255,255).
"""

import argparse
import numpy as np
from PIL import Image
import os

def extract_simple_lineart(input_path, output_path, line_color=(10, 10, 10), bg_color=(255, 255, 255)):
    """
    Extract lineart by converting non-line pixels to background color
    
    Args:
        input_path: Path to input image
        output_path: Path to save extracted lineart
        line_color: RGB color of the line art (default: (10, 10, 10))
        bg_color: RGB color for background (default: (255, 255, 255))
    """
    # Load image
    image = Image.open(input_path)
    
    # Convert to RGB if not already
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Convert to numpy array
    img_array = np.array(image)
    
    print(f"Processing image: {input_path} ({img_array.shape[1]}x{img_array.shape[0]})")
    
    # Create mask for line art pixels
    line_mask = np.all(img_array == line_color, axis=2)
    
    # Create output array filled with background color
    output_array = np.full_like(img_array, bg_color)
    
    # Keep line art pixels unchanged
    output_array[line_mask] = line_color
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Convert back to PIL Image and save
    output_image = Image.fromarray(output_array.astype(np.uint8))
    output_image.save(output_path)
    
    print(f"Simple lineart extracted to: {output_path}")
    
    # Print statistics
    total_pixels = img_array.shape[0] * img_array.shape[1]
    line_pixels = np.sum(line_mask)
    print(f"Line art pixels: {line_pixels} / {total_pixels} ({line_pixels/total_pixels*100:.2f}%)")

def main():
    parser = argparse.ArgumentParser(
        description="Extract lineart from images with specific line color",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python extract_simple_lineart.py input.jpg output.png
    python extract_simple_lineart.py input.jpg output.png --line-color 10 10 10
    python extract_simple_lineart.py input.jpg output.png --bg-color 255 255 255
        """
    )
    parser.add_argument("input", help="Input image path")
    parser.add_argument("output", help="Output lineart path")
    parser.add_argument("--line-color", nargs=3, type=int, default=[10, 10, 10],
                       help="RGB color of line art (default: 10 10 10)")
    parser.add_argument("--bg-color", nargs=3, type=int, default=[255, 255, 255],
                       help="RGB color for background (default: 255 255 255)")
    
    args = parser.parse_args()
    
    try:
        extract_simple_lineart(
            args.input,
            args.output,
            tuple(args.line_color),
            tuple(args.bg_color)
        )
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())