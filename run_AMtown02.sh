#!/bin/bash
# AAE5303 - MARS-LVIG AMtown02 运行脚本
# 团队: ALateFix

set -e
cd "$(dirname "$0")"

# 配置
BAG="${1:-data/AMtown02.bag}"
VOCAB="Vocabulary/ORBvoc.txt"
CONFIG="Examples/Monocular/AMtown02_Mono.yaml"
OUTPUT_DIR="${2:-.}"

echo "=== Step 1: 提取 ground_truth ==="
if [[ -f "$BAG" ]]; then
    python3 scripts/extract_ground_truth.py "$BAG" -o "$OUTPUT_DIR/ground_truth.txt"
else
    echo "警告: 未找到 $BAG，跳过 ground_truth 提取。"
    echo "请从 MARS-LVIG 下载 AMtown02: https://drive.google.com/file/d/1rU-1B_B6KJ3dEP6DUooFF3pgMNEOEkcW/view"
fi

echo ""
echo "=== Step 2: 启动 ORB-SLAM3 (需手动) ==="
echo "终端1: roscore"
echo "终端2: ./Examples_old/ROS/ORB_SLAM3/Mono_Compressed $VOCAB $CONFIG"
echo "终端3: rosbag play --pause $BAG /left_camera/image/compressed:=/camera/image_raw/compressed"
echo ""
echo "在 ORB-SLAM3 就绪后，在终端3按空格开始播放。"
echo "运行结束后，CameraTrajectory.txt 和 KeyFrameTrajectory.txt 会保存在运行目录。"
echo ""
echo "=== Step 3: 评估 (运行结束后执行) ==="
echo "python3 scripts/evaluate_vo_accuracy.py --groundtruth $OUTPUT_DIR/ground_truth.txt --estimated CameraTrajectory.txt --workdir evaluation_results --json-out evaluation_results/metrics.json"
echo ""
echo "=== Step 4: 生成 leaderboard 提交 ==="
echo "python3 scripts/update_leaderboard_json.py"
