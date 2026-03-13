# AAE5303 Leaderboard Submission Guide

**Team**: ALateFix  
**GitHub**: https://github.com/shentonyan/AAE5303_assignment2_orbslam

---

## 1. Dataset

- **MARS-LVIG AMtown02**: https://drive.google.com/file/d/1rU-1B_B6KJ3dEP6DUooFF3pgMNEOEkcW/view
- Place the bag at `data/AMtown02.bag`

## 2. Run Pipeline

### 2.1 Extract Ground Truth

```bash
python3 scripts/extract_ground_truth.py data/AMtown02.bag -o ground_truth.txt
```

RTK topic: `/dji_osdk_ros/rtk_position`.

### 2.2 Run ORB-SLAM3

**Terminal 1:**
```bash
source /opt/ros/noetic/setup.bash
roscore
```

**Terminal 2:**
```bash
source /opt/ros/noetic/setup.bash
cd <project_root>
./Examples_old/ROS/ORB_SLAM3/Mono_Compressed \
    Vocabulary/ORBvoc.txt \
    Examples/Monocular/AMtown02_Mono.yaml
```

**Terminal 3:**
```bash
source /opt/ros/noetic/setup.bash
cd <project_root>
rosbag play --pause data/AMtown02.bag \
    /left_camera/image/compressed:=/camera/image_raw/compressed
```

Press **Space** in Terminal 3 when ORB-SLAM3 is ready. After Ctrl+C, you will get:
- `CameraTrajectory.txt` (full-frame trajectory, **for evaluation**)
- `KeyFrameTrajectory.txt` (keyframe trajectory)

### 2.3 Evaluate

```bash
python3 scripts/evaluate_vo_accuracy.py \
    --groundtruth ground_truth.txt \
    --estimated CameraTrajectory.txt \
    --t-max-diff 0.1 \
    --delta-m 10 \
    --workdir evaluation_results \
    --json-out evaluation_results/metrics.json
```

### 2.4 Update Leaderboard Submission

```bash
python3 scripts/update_leaderboard_json.py
```

Generates `submission/ALateFix_leaderboard.json`.

## 3. Submission Files

| File | Description |
|------|-------------|
| `submission/ALateFix_leaderboard.json` | Leaderboard submission JSON |
| `results/CameraTrajectory.txt` | Full-frame trajectory (TUM) |
| `results/ground_truth.txt` | RTK ground truth (TUM) |
| `results/plots/` | Evaluation trajectory plots |

## 4. Full-Frame Trajectory

The course requires **CameraTrajectory.txt** (full-frame), not KeyFrameTrajectory.txt.

This repo modifies:
1. `src/System.cc`: Allow monocular mode to call `SaveTrajectoryTUM`
2. `Examples_old/ROS/ORB_SLAM3/src/ros_mono_compressed.cc`: Call `SaveTrajectoryTUM("CameraTrajectory.txt")` after `Shutdown()`

## 5. Validate Submission Format

```python
import json
with open("submission/ALateFix_leaderboard.json", "r", encoding="utf-8") as f:
    s = json.load(f)
assert "group_name" in s and s["group_name"] == "ALateFix"
assert "project_private_repo_url" in s
assert "metrics" in s
for k in ["ate_rmse_m", "rpe_trans_drift_m_per_m", "rpe_rot_drift_deg_per_100m", "completeness_pct"]:
    assert k in s["metrics"]
print("Submission format is valid!")
```
