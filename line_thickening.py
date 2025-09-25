#!/usr/bin/env python3
"""
Line thickening algorithm to ensure line pixels have at least 1px adjacent thickness.
Applies 3x3 grid logic to fix incomplete line segments in binary images.
"""

import numpy as np
from PIL import Image
import cv2
import os


def apply_line_thickening(img_array, line_color=(10, 10, 10), bg_color=(255, 255, 255), iterations=1):
    """
    Apply line thickening algorithm to ensure lines have at least 1px adjacent thickness.

    Uses 3x3 grid logic: if diagonal pixels exist without proper horizontal/vertical
    connections forming 3-pixel blocks, automatically fills gaps.

    Args:
        img_array: Input image as numpy array (H, W, 3)
        line_color: RGB color of line pixels (default: (10, 10, 10))
        bg_color: RGB color of background pixels (default: (255, 255, 255))
        iterations: Number of thickening iterations to apply (default: 1)

    Returns:
        numpy array: Thickened image
    """
    # Convert to binary mask for processing
    line_mask = np.all(img_array == line_color, axis=2)

    # Work with a copy to avoid modifying original during iteration
    result_mask = line_mask.copy()

    for iteration in range(iterations):
        # Pad the mask to handle border pixels
        padded_mask = np.pad(result_mask, 1, mode='constant', constant_values=False)
        new_mask = result_mask.copy()

        # Iterate through each pixel (excluding borders)
        for y in range(1, padded_mask.shape[0] - 1):
            for x in range(1, padded_mask.shape[1] - 1):
                # Extract 3x3 neighborhood
                neighborhood = padded_mask[y-1:y+2, x-1:x+2]

                # Get positions: center, cardinal directions, and diagonals
                center = neighborhood[1, 1]
                top = neighborhood[0, 1]
                bottom = neighborhood[2, 1]
                left = neighborhood[1, 0]
                right = neighborhood[1, 2]
                top_left = neighborhood[0, 0]
                top_right = neighborhood[0, 2]
                bottom_left = neighborhood[2, 0]
                bottom_right = neighborhood[2, 2]

                # Original image coordinates (adjust for padding)
                orig_y, orig_x = y - 1, x - 1

                # Skip if out of bounds in original image
                if orig_y >= result_mask.shape[0] or orig_x >= result_mask.shape[1]:
                    continue

                # Check for thin diagonal connections that need thickening
                needs_fill = False

                # Case 1: Top-left to bottom-right diagonal
                if top_left and bottom_right and not center:
                    # Check if there's insufficient horizontal/vertical support
                    horizontal_support = (left and top) or (right and bottom) or (left and bottom) or (right and top)
                    if not horizontal_support:
                        needs_fill = True

                # Case 2: Top-right to bottom-left diagonal
                if top_right and bottom_left and not center:
                    # Check if there's insufficient horizontal/vertical support
                    horizontal_support = (right and top) or (left and bottom) or (right and bottom) or (left and top)
                    if not horizontal_support:
                        needs_fill = True

                # Case 3: Fill gaps in horizontal and vertical lines
                # Pattern: 0 0 0 / 1 0 1 / 0 0 0 (horizontal gap)
                if not center and left and right and not (top or bottom):
                    needs_fill = True

                # Pattern: 0 1 0 / 0 0 0 / 0 1 0 (vertical gap)
                if not center and top and bottom and not (left or right):
                    needs_fill = True

                # Case 4: Fill gaps in diagonal connections
                # Pattern: 1 0 0 / 0 0 1 / 0 0 0 (top-left to center-right diagonal)
                if not center and top_left and right and not (top or left or bottom or bottom_right):
                    needs_fill = True

                # Pattern: 0 0 1 / 1 0 0 / 0 0 0 (top-right to center-left diagonal)
                if not center and top_right and left and not (top or right or bottom or bottom_left):
                    needs_fill = True

                # Pattern: 0 0 0 / 0 0 1 / 1 0 0 (center-right to bottom-left diagonal)
                if not center and right and bottom_left and not (top or left or bottom or top_left):
                    needs_fill = True

                # Pattern: 0 0 0 / 1 0 0 / 0 0 1 (center-left to bottom-right diagonal)
                if not center and left and bottom_right and not (top or right or bottom or top_right):
                    needs_fill = True

                # Case 5: Single pixel connections that create thin spots
                if center:
                    # Count connected cardinal neighbors
                    cardinal_neighbors = sum([top, bottom, left, right])
                    # Count connected diagonal neighbors
                    diagonal_neighbors = sum([top_left, top_right, bottom_left, bottom_right])

                    # If we have diagonal connections but insufficient cardinal support
                    if diagonal_neighbors > 0 and cardinal_neighbors < 2:
                        # Fill in cardinal directions to strengthen the connection
                        if top_left and not (top or left):
                            new_mask[max(0, orig_y-1), orig_x] = True  # Fill top
                            new_mask[orig_y, max(0, orig_x-1)] = True  # Fill left
                        if top_right and not (top or right):
                            new_mask[max(0, orig_y-1), orig_x] = True  # Fill top
                            new_mask[orig_y, min(new_mask.shape[1]-1, orig_x+1)] = True  # Fill right
                        if bottom_left and not (bottom or left):
                            new_mask[min(new_mask.shape[0]-1, orig_y+1), orig_x] = True  # Fill bottom
                            new_mask[orig_y, max(0, orig_x-1)] = True  # Fill left
                        if bottom_right and not (bottom or right):
                            new_mask[min(new_mask.shape[0]-1, orig_y+1), orig_x] = True  # Fill bottom
                            new_mask[orig_y, min(new_mask.shape[1]-1, orig_x+1)] = True  # Fill right

                # Fill the center pixel if needed for diagonal connections
                if needs_fill:
                    new_mask[orig_y, orig_x] = True

        result_mask = new_mask

    # Convert back to RGB image
    output_array = np.full_like(img_array, bg_color)
    output_array[result_mask] = line_color

    return output_array


def cleanup_isolated_pixels(img_array, line_color=(10, 10, 10), bg_color=(255, 255, 255)):
    """
    Clean up isolated pixels based on 4-connected degree analysis.
    Removes pixels that have degree=3 (only 1 out of 4 neighbors is black).

    Args:
        img_array: Input image as numpy array (H, W, 3)
        line_color: RGB color of line pixels (default: (10, 10, 10))
        bg_color: RGB color of background pixels (default: (255, 255, 255))

    Returns:
        numpy array: Cleaned image
    """
    # Convert to binary mask for processing
    line_mask = np.all(img_array == line_color, axis=2)
    result_mask = line_mask.copy()

    height, width = line_mask.shape
    removed_count = 0

    # Iterate through each pixel
    for y in range(height):
        for x in range(width):
            if not line_mask[y, x]:
                continue  # Skip background pixels

            # Check 4-connected neighbors
            neighbors = []
            # Top
            if y > 0:
                neighbors.append(line_mask[y-1, x])
            # Bottom
            if y < height - 1:
                neighbors.append(line_mask[y+1, x])
            # Left
            if x > 0:
                neighbors.append(line_mask[y, x-1])
            # Right
            if x < width - 1:
                neighbors.append(line_mask[y, x+1])

            # Count black neighbors
            black_neighbors = sum(neighbors)
            total_neighbors = len(neighbors)

            # If degree=3 (3 edges not connected to black points)
            # This means total_neighbors - black_neighbors = 3
            # Or equivalently, black_neighbors = 1 (for interior pixels with 4 neighbors)
            if total_neighbors == 4 and black_neighbors == 1:
                result_mask[y, x] = False  # Remove this pixel
                removed_count += 1
            # Handle edge pixels (less than 4 neighbors)
            elif total_neighbors < 4 and black_neighbors == 1:
                result_mask[y, x] = False  # Remove this pixel
                removed_count += 1

    # Convert back to RGB image
    output_array = np.full_like(img_array, bg_color)
    output_array[result_mask] = line_color

    print(f"Cleanup isolated pixels: removed {removed_count} pixels with degree=3")

    return output_array


def remove_noise_components(img_array, line_color=(10, 10, 10), bg_color=(255, 255, 255), min_component_size=15, method='connected_components'):
    """
    Remove noise/small components from line art image.

    Args:
        img_array: Input image as numpy array (H, W, 3)
        line_color: RGB color of line pixels (default: (10, 10, 10))
        bg_color: RGB color of background pixels (default: (255, 255, 255))
        min_component_size: Minimum size of components to keep (pixels)
        method: Noise removal method ('connected_components', 'morphology', 'median')

    Returns:
        numpy array: Cleaned image
    """
    # Convert to binary mask for processing
    line_mask = np.all(img_array == line_color, axis=2).astype(np.uint8)

    if method == 'connected_components':
        # Use connected components analysis to remove small components
        # Find all connected components
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(line_mask, connectivity=8)

        # Create output mask
        cleaned_mask = np.zeros_like(line_mask)

        # Keep components larger than threshold (skip label 0 which is background)
        for label in range(1, num_labels):
            component_size = stats[label, cv2.CC_STAT_AREA]
            if component_size >= min_component_size:
                cleaned_mask[labels == label] = 1

        print(f"Connected components: {num_labels - 1} found, kept {np.sum([stats[i, cv2.CC_STAT_AREA] >= min_component_size for i in range(1, num_labels)])} components >= {min_component_size} pixels")

    elif method == 'morphology':
        # Use morphological opening to remove noise
        kernel_size = max(1, min_component_size // 4)  # Adaptive kernel size
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
        cleaned_mask = cv2.morphologyEx(line_mask, cv2.MORPH_OPEN, kernel)
        print(f"Morphological opening applied with kernel size {kernel_size}x{kernel_size}")

    elif method == 'median':
        # Use median filter to remove salt-and-pepper noise
        kernel_size = max(3, min_component_size // 2)
        if kernel_size % 2 == 0:  # Ensure odd kernel size
            kernel_size += 1
        cleaned_mask = cv2.medianBlur(line_mask, kernel_size)
        print(f"Median filter applied with kernel size {kernel_size}x{kernel_size}")

    else:
        raise ValueError(f"Unknown method: {method}. Use 'connected_components', 'morphology', or 'median'")

    # Convert back to RGB image
    output_array = np.full_like(img_array, bg_color)
    output_array[cleaned_mask == 1] = line_color

    # Print statistics
    original_pixels = np.sum(line_mask)
    cleaned_pixels = np.sum(cleaned_mask)
    removed_pixels = original_pixels - cleaned_pixels
    print(f"Noise removal: {original_pixels} → {cleaned_pixels} pixels (-{removed_pixels}, -{removed_pixels/original_pixels*100:.1f}%)")

    return output_array


def thicken_lineart_file(input_path, output_path, line_color=(10, 10, 10), bg_color=(255, 255, 255), iterations=1):
    """
    Apply line thickening to an image file.

    Args:
        input_path: Path to input image
        output_path: Path to save thickened image
        line_color: RGB color of line pixels (default: (10, 10, 10))
        bg_color: RGB color of background pixels (default: (255, 255, 255))
        iterations: Number of thickening iterations (default: 1)
    """
    # Load image
    image = Image.open(input_path)

    # Convert to RGB if not already
    if image.mode != 'RGB':
        image = image.convert('RGB')

    # Convert to numpy array
    img_array = np.array(image)

    print(f"Applying line thickening to: {input_path} ({img_array.shape[1]}x{img_array.shape[0]})")
    print(f"Line color: {line_color}, Background color: {bg_color}, Iterations: {iterations}")

    # Count original line pixels
    original_line_mask = np.all(img_array == line_color, axis=2)
    original_line_pixels = np.sum(original_line_mask)

    # Apply thickening
    thickened_array = apply_line_thickening(img_array, line_color, bg_color, iterations)

    # Count new line pixels
    new_line_mask = np.all(thickened_array == line_color, axis=2)
    new_line_pixels = np.sum(new_line_mask)

    # Create output directory if needed
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Save result
    output_image = Image.fromarray(thickened_array.astype(np.uint8))
    output_image.save(output_path)

    print(f"Line thickening completed. Saved to: {output_path}")
    print(f"Line pixels: {original_line_pixels} -> {new_line_pixels} (+{new_line_pixels - original_line_pixels})")

    return thickened_array


def cleanup_isolated_pixels_from_file(input_path, output_path, line_color=(10, 10, 10), bg_color=(255, 255, 255)):
    """
    Clean up isolated pixels from an image file using 4-connected degree analysis.

    Args:
        input_path: Path to input image
        output_path: Path to save cleaned image
        line_color: RGB color of line pixels (default: (10, 10, 10))
        bg_color: RGB color of background pixels (default: (255, 255, 255))
    """
    # Load image
    image = Image.open(input_path)

    # Convert to RGB if not already
    if image.mode != 'RGB':
        image = image.convert('RGB')

    # Convert to numpy array
    img_array = np.array(image)

    print(f"Cleaning up isolated pixels from: {input_path} ({img_array.shape[1]}x{img_array.shape[0]})")

    # Apply cleanup
    cleaned_array = cleanup_isolated_pixels(img_array, line_color, bg_color)

    # Create output directory if needed
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Save result
    output_image = Image.fromarray(cleaned_array.astype(np.uint8))
    output_image.save(output_path)

    print(f"Cleanup completed. Saved to: {output_path}")

    return cleaned_array


def remove_noise_from_file(input_path, output_path, line_color=(10, 10, 10), bg_color=(255, 255, 255), min_component_size=10, method='connected_components'):
    """
    Remove noise from an image file using various algorithms.

    Args:
        input_path: Path to input image
        output_path: Path to save cleaned image
        line_color: RGB color of line pixels (default: (10, 10, 10))
        bg_color: RGB color of background pixels (default: (255, 255, 255))
        min_component_size: Minimum size of components to keep (pixels)
        method: Noise removal method ('connected_components', 'morphology', 'median')
    """
    # Load image
    image = Image.open(input_path)

    # Convert to RGB if not already
    if image.mode != 'RGB':
        image = image.convert('RGB')

    # Convert to numpy array
    img_array = np.array(image)

    print(f"Removing noise from: {input_path} ({img_array.shape[1]}x{img_array.shape[0]})")
    print(f"Method: {method}, Min component size: {min_component_size} pixels")

    # Apply noise removal
    cleaned_array = remove_noise_components(img_array, line_color, bg_color, min_component_size, method)

    # Create output directory if needed
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Save result
    output_image = Image.fromarray(cleaned_array.astype(np.uint8))
    output_image.save(output_path)

    print(f"Noise removal completed. Saved to: {output_path}")

    return cleaned_array


def process_complete_pipeline(input_path, output_path, line_color=(10, 10, 10), bg_color=(255, 255, 255),
                            thicken_iterations=1, remove_noise=True, min_component_size=10, noise_method='connected_components',
                            cleanup_isolated=True):
    """
    Complete pipeline: line thickening followed by noise removal and cleanup.

    Args:
        input_path: Path to input image
        output_path: Path to save final processed image
        line_color: RGB color of line pixels (default: (10, 10, 10))
        bg_color: RGB color of background pixels (default: (255, 255, 255))
        thicken_iterations: Number of thickening iterations
        remove_noise: Whether to apply noise removal after thickening
        min_component_size: Minimum size of components to keep (pixels)
        noise_method: Noise removal method
        cleanup_isolated: Whether to apply isolated pixel cleanup
    """
    # Load image
    image = Image.open(input_path)

    # Convert to RGB if not already
    if image.mode != 'RGB':
        image = image.convert('RGB')

    # Convert to numpy array
    img_array = np.array(image)

    print(f"Processing complete pipeline: {input_path} ({img_array.shape[1]}x{img_array.shape[0]})")
    print(f"Step 1: Line thickening (iterations: {thicken_iterations})")

    # Step 1: Apply line thickening
    thickened_array = apply_line_thickening(img_array, line_color, bg_color, thicken_iterations)

    # Step 2: Apply noise removal if requested
    if remove_noise:
        print(f"Step 2: Noise removal (method: {noise_method}, min size: {min_component_size})")
        current_array = remove_noise_components(thickened_array, line_color, bg_color, min_component_size, noise_method)
    else:
        current_array = thickened_array
        print("Step 2: Skipped noise removal")

    # Step 3: Apply isolated pixel cleanup if requested
    if cleanup_isolated:
        print("Step 3: Cleanup isolated pixels (4-connected degree=3)")
        final_array = cleanup_isolated_pixels(current_array, line_color, bg_color)
    else:
        final_array = current_array
        print("Step 3: Skipped isolated pixel cleanup")

    # Create output directory if needed
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Save result
    output_image = Image.fromarray(final_array.astype(np.uint8))
    output_image.save(output_path)

    print(f"Complete pipeline finished. Saved to: {output_path}")

    return final_array


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Apply line thickening and noise removal to line art images",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Line thickening only
    python line_thickening.py input.png output.png
    python line_thickening.py input.png output.png --iterations 2

    # Noise removal only
    python line_thickening.py input.png output.png --noise-only --min-size 5

    # Complete pipeline (thickening + noise removal)
    python line_thickening.py input.png output.png --pipeline --noise-method connected_components

    # Custom colors
    python line_thickening.py input.png output.png --line-color 0 0 0 --bg-color 255 255 255
        """
    )
    parser.add_argument("input", help="Input image path")
    parser.add_argument("output", help="Output processed image path")
    parser.add_argument("--line-color", nargs=3, type=int, default=[10, 10, 10],
                       help="RGB color of line pixels (default: 10 10 10)")
    parser.add_argument("--bg-color", nargs=3, type=int, default=[255, 255, 255],
                       help="RGB color of background pixels (default: 255 255 255)")
    parser.add_argument("--iterations", type=int, default=1,
                       help="Number of thickening iterations (default: 1)")

    # Noise removal options
    parser.add_argument("--noise-only", action="store_true",
                       help="Apply noise removal only (skip thickening)")
    parser.add_argument("--pipeline", action="store_true",
                       help="Apply complete pipeline (thickening + noise removal)")
    parser.add_argument("--min-size", type=int, default=10,
                       help="Minimum component size to keep when removing noise (default: 10)")
    parser.add_argument("--noise-method", choices=['connected_components', 'morphology', 'median'],
                       default='connected_components',
                       help="Noise removal method (default: connected_components)")

    args = parser.parse_args()

    try:
        line_color = tuple(args.line_color)
        bg_color = tuple(args.bg_color)

        if args.noise_only:
            # Apply noise removal only
            remove_noise_from_file(
                args.input,
                args.output,
                line_color,
                bg_color,
                args.min_size,
                args.noise_method
            )
        elif args.pipeline:
            # Apply complete pipeline
            process_complete_pipeline(
                args.input,
                args.output,
                line_color,
                bg_color,
                args.iterations,
                True,  # remove_noise=True
                args.min_size,
                args.noise_method
            )
        else:
            # Apply thickening only (default behavior)
            thicken_lineart_file(
                args.input,
                args.output,
                line_color,
                bg_color,
                args.iterations
            )
    except Exception as e:
        print(f"Error: {e}")
        exit(1)