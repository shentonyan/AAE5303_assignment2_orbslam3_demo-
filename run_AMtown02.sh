#!/bin/bash
# AAE5303 - MARS-LVIG AMtown02 run script
# Team: ALateFix

set -e
cd "$(dirname "$0")"

# Config
BAG="${1:-data/AMtown02.bag}"
VOCAB="Vocabulary/ORBvoc.txt"
CONFIG="Examples/Monocular/AMtown02_Mono.yaml"
OUTPUT_DIR="${2:-.}"

echo "=== Step 1: Extract ground_truth ==="
if [[ -f "$BAG" ]]; then
    python3 scripts/extract_ground_truth.py "$BAG" -o "$OUTPUT_DIR/ground_truth.txt"
else
    echo "Warning: $BAG not found, skipping ground truth extraction."
    echo "Download AMtown02 from MARS-LVIG: https://drive.google.com/file/d/1rU-1B_B6KJ3dEP6DUooFF3pgMNEOEkcW/view"
fi

echo ""
echo "=== Step 2: Start ORB-SLAM3 (manual) ==="
echo "Terminal 1: roscore"
echo "Terminal 2: ./Examples_old/ROS/ORB_SLAM3/Mono_Compressed $VOCAB $CONFIG"
echo "Terminal 3: rosbag play --pause $BAG /left_camera/image/compressed:=/camera/image_raw/compressed"
echo ""
echo "Press Space in Terminal 3 when ORB-SLAM3 is ready."
echo "After Ctrl+C, CameraTrajectory.txt and KeyFrameTrajectory.txt will be saved."
echo ""
echo "=== Step 3: Evaluate (after run completes) ==="
echo "python3 scripts/evaluate_vo_accuracy.py --groundtruth $OUTPUT_DIR/ground_truth.txt --estimated CameraTrajectory.txt --workdir evaluation_results --json-out evaluation_results/metrics.json"
echo ""
echo "=== Step 4: Update leaderboard submission ==="
echo "python3 scripts/update_leaderboard_json.py"
