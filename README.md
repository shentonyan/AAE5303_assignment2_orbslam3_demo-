# AAE5303 Assignment 2 - ORB-SLAM3 Monocular VO

**Team**: ALateFix  
**Repository**: [https://github.com/shentonyan/AAE5303_assignment2_orbslam](https://github.com/shentonyan/AAE5303_assignment2_orbslam)

Monocular visual odometry based on ORB-SLAM3, evaluated on the MARS-LVIG AMtown02 dataset.

---

## Project Structure

```
.
├── README.md                           # This file
├── run_AMtown02.sh                     # Run guide script
├── evo_headless_config.json            # Headless evaluation config
│
├── scripts/                            # Scripts
│   ├── extract_ground_truth.py         # Extract RTK ground truth from bag
│   ├── evaluate_vo_accuracy.py        # Evaluate (ATE/RPE/Completeness)
│   └── update_leaderboard_json.py     # Update leaderboard submission
│
├── submission/                         # Leaderboard submission
│   ├── ALateFix_leaderboard.json       # Submission file (with metrics)
│   └── submission_template.json       # Template
│
├── Examples/Monocular/                 # Camera config
│   └── AMtown02_Mono.yaml              # AMtown02 parameters
│
├── src/                                # Modified source (ORB-SLAM3)
│   └── System.cc                       # Full-frame trajectory support
│
├── Examples_old/ROS/ORB_SLAM3/src/     # Modified ROS node
│   └── ros_mono_compressed.cc          # Saves CameraTrajectory.txt
│
├── results/                            # Run results
│   ├── CameraTrajectory.txt            # Full-frame estimated trajectory
│   ├── ground_truth.txt                # RTK ground truth
│   ├── metrics.json                   # Evaluation metrics
│   └── plots/                          # Trajectory plots
│       ├── ape_trajectory_map.png      # ATE trajectory top view
│       ├── ape_trajectory_raw.png      # ATE error curve
│       ├── rpe_trans_trajectory_*.png  # RPE translation
│       └── rpe_rot_trajectory_*.png    # RPE rotation
│
└── docs/                               # Documentation
    └── LEADERBOARD.md                  # Leaderboard submission guide
```

---

## Quick Start

### Requirements

- ROS Noetic
- ORB-SLAM3 (full project must be built first)
- evo (`pip install evo`)
- MARS-LVIG AMtown02 bag

### 1. Download Dataset

Download from [MARS-LVIG AMtown02](https://drive.google.com/file/d/1rU-1B_B6KJ3dEP6DUooFF3pgMNEOEkcW/view) and place at `data/AMtown02.bag`.

### 2. Extract Ground Truth

```bash
source /opt/ros/noetic/setup.bash
python3 scripts/extract_ground_truth.py data/AMtown02.bag -o ground_truth.txt
```

### 3. Run ORB-SLAM3

```bash
# Terminal 1
roscore

# Terminal 2
./Examples_old/ROS/ORB_SLAM3/Mono_Compressed Vocabulary/ORBvoc.txt Examples/Monocular/AMtown02_Mono.yaml

# Terminal 3
rosbag play --pause data/AMtown02.bag /left_camera/image/compressed:=/camera/image_raw/compressed
```

Press **Space** in Terminal 3 when ORB-SLAM3 is ready. Press Ctrl+C to stop; `CameraTrajectory.txt` will be saved.

### 4. Evaluate

```bash
python3 scripts/evaluate_vo_accuracy.py \
    --groundtruth ground_truth.txt \
    --estimated CameraTrajectory.txt \
    --workdir evaluation_results \
    --json-out evaluation_results/metrics.json

python3 scripts/update_leaderboard_json.py
```

> Evaluation generates `evaluation_results/` and trajectory plots. The `results/` folder in this repo contains pre-run results for reference.

---

## Evaluation Results

| Metric | Value |
|--------|-------|
| ATE RMSE | 6.71 m |
| RPE Trans Drift | 1.34 m/m |
| RPE Rot Drift | 40.65 deg/100m |
| Completeness | 92.91 % |

Trajectory plots: `results/plots/`.

---

## Code Modifications

The course requires **full-frame trajectory** (CameraTrajectory.txt) for evaluation:

1. **src/System.cc**: Removed monocular restriction on `SaveTrajectoryTUM`
2. **ros_mono_compressed.cc**: Calls `SaveTrajectoryTUM("CameraTrajectory.txt")` after `Shutdown()`

Overwrite the files in `src/` and `Examples_old/` to the corresponding ORB-SLAM3 paths, then rebuild.

---

## Leaderboard Submission

Submission file: `submission/ALateFix_leaderboard.json`  
See [docs/LEADERBOARD.md](docs/LEADERBOARD.md) for details.

---

## Configuration

- **RTK topic**: `/dji_osdk_ros/rtk_position`
- **Camera topic**: `/left_camera/image/compressed` (remap to `/camera/image_raw/compressed`)
- **Camera params**: Same as HKisland config
