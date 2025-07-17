#!/bin/bash

# Lineart Extraction Script Selector
# Choose between AI-based and simple pixel-based extraction

echo "=== Lineart Extraction Tool ==="
echo "1. AI-based extraction (extract_lineart.py)"
echo "2. Simple pixel-based extraction (extract_simple_lineart.py)"
echo "3. Extract frames (extract_frames.py)"
echo

read -p "Choose extraction method (1-3): " choice

case $choice in
    1)
        echo "Using AI-based lineart extraction..."
        if [ $# -eq 0 ]; then
            echo "Usage: $0 [input_image] [output_image] [additional_args...]"
            echo "Example: $0 input.jpg output.png --coarse --threshold 100"
            exit 1
        fi
        python3 extract_lineart.py "$@"
        ;;
    2)
        echo "Using simple pixel-based extraction..."
        if [ $# -eq 0 ]; then
            echo "Usage: $0 [input_image] [output_image] [additional_args...]"
            echo "Example: $0 input.jpg output.png --line-color 10 10 10"
            exit 1
        fi
        python3 extract_simple_lineart.py "$@"
        ;;
    3)
        echo "Using frame extraction..."
        python3 extract_frames.py "$@"
        ;;
    *)
        echo "Invalid choice. Please select 1, 2, or 3."
        exit 1
        ;;
esac