#!/bin/bash

# ============================================================================
# 批次線稿提取腳本 - 對 FlatColor_testcases 進行線稿提取
# ============================================================================

# Configuration
INPUT_DIR="FlatColor_testcases"
OUTPUT_DIR="Flatcolor_testcases_lineart"
EXTRACTION_METHOD="ai"  # "ai" for AI-based or "simple" for pixel-based
THRESHOLD=200
FORMAT="rgb"  # binary, rgb, or rgba

# ============================================================================

# 創建輸出目錄
mkdir -p "$OUTPUT_DIR"

echo "============================================================================"
echo "Starting batch lineart extraction for FlatColor_testcases..."
echo "Input directory: $INPUT_DIR"
echo "Output directory: $OUTPUT_DIR"
echo "Extraction method: $EXTRACTION_METHOD"
echo "============================================================================"
echo

# 檢查線稿提取腳本是否存在
if [ "$EXTRACTION_METHOD" = "ai" ]; then
    EXTRACT_SCRIPT="extract_lineart.py"
    if [ ! -f "$EXTRACT_SCRIPT" ]; then
        echo "Error: $EXTRACT_SCRIPT not found!"
        exit 1
    fi

    # 檢查模型是否存在
    if [ ! -f "models/sk_model.pth" ]; then
        echo "Error: AI models not found. Please run: python models/download_models.py"
        exit 1
    fi
else
    EXTRACT_SCRIPT="extract_simple_lineart.py"
    if [ ! -f "$EXTRACT_SCRIPT" ]; then
        echo "Error: $EXTRACT_SCRIPT not found!"
        exit 1
    fi
fi

# 線稿提取函數
extract_lineart() {
    local input_file="$1"
    local output_file="$2"

    if [ "$EXTRACTION_METHOD" = "ai" ]; then
        python "$EXTRACT_SCRIPT" "$input_file" "$output_file" --threshold "$THRESHOLD" --format "$FORMAT"
    else
        python "$EXTRACT_SCRIPT" "$input_file" "$output_file"
    fi

    return $?
}

# 處理每個測試案例目錄
total_processed=0
total_success=0
total_failed=0

for case_dir in "$INPUT_DIR"/*/; do
    if [ ! -d "$case_dir" ]; then
        continue
    fi

    case_name=$(basename "$case_dir")
    echo "============================"
    echo "Processing case: $case_name"

    # 創建對應的輸出目錄
    case_output_dir="$OUTPUT_DIR/$case_name"
    mkdir -p "$case_output_dir"

    # 找到所有 scene_*.png 文件並按順序處理
    scene_files=($(ls "$case_dir"scene_*.png 2>/dev/null | sort -V))

    if [ ${#scene_files[@]} -eq 0 ]; then
        echo "  Warning: No scene files found in $case_name, skipping..."
        continue
    fi

    echo "  Found ${#scene_files[@]} scene files"

    case_processed=0
    case_success=0
    case_failed=0

    # 處理每個場景文件
    for input_file in "${scene_files[@]}"; do
        if [ ! -f "$input_file" ]; then
            continue
        fi

        filename=$(basename "$input_file")
        # 生成輸出文件名：scene_A0001.png -> scene_A0001_lineart.png
        output_filename="${filename%.png}_lineart.png"
        output_file="$case_output_dir/$output_filename"

        echo "  Processing: $filename -> $output_filename"

        # 提取線稿
        if extract_lineart "$input_file" "$output_file"; then
            echo "    ✅ Success"
            case_success=$((case_success + 1))
            total_success=$((total_success + 1))
        else
            echo "    ❌ Failed"
            case_failed=$((case_failed + 1))
            total_failed=$((total_failed + 1))
        fi

        case_processed=$((case_processed + 1))
        total_processed=$((total_processed + 1))
    done

    echo "  Case summary: $case_processed processed, $case_success success, $case_failed failed"
    echo
done

echo "============================================================================"
echo "Batch lineart extraction completed!"
echo "Total files processed: $total_processed"
echo "Successful extractions: $total_success"
echo "Failed extractions: $total_failed"
echo "Results saved in: $OUTPUT_DIR"
echo "============================================================================"