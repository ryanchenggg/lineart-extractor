import cv2
import os

# Video file path
video_path = '/storage/Internal_NAS/ryan/exps_m/SketchColour/AnitaDataset/hope/16_a/16_a_colorize.mp4'
output_dir = '/storage/Internal_NAS/ryan/exps_m/SketchColour/AnitaDataset/hope/16_a/results'

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Open video file
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print(f'Error: Could not open video file {video_path}')
    exit()

# Get video properties
fps = cap.get(cv2.CAP_PROP_FPS)
frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

print(f'Video properties:')
print(f'  FPS: {fps}')
print(f'  Total frames: {frame_count}')
print(f'  Resolution: {width}x{height}')
print(f'')

frame_num = 0
while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Save frame as PNG with 4-digit padding
    output_filename = f'{frame_num:04d}.png'
    output_path = os.path.join(output_dir, output_filename)
    cv2.imwrite(output_path, frame)
    
    print(f'Extracted frame {frame_num+1}/{frame_count}: {output_filename}')
    frame_num += 1

cap.release()
print(f'')
print(f'Extraction complete! {frame_num} frames saved to {output_dir}')