# AAE5303 Assignment 2 - ORB-SLAM3 Monocular VO

**团队**: ALateFix  
**仓库**: [https://github.com/shentonyan/AAE5303_assignment2_orbslam](https://github.com/shentonyan/AAE5303_assignment2_orbslam)

基于 ORB-SLAM3 的单目视觉里程计，在 MARS-LVIG AMtown02 数据集上运行与评估。

---

## 📁 项目结构

```
.
├── README.md                           # 本文件
├── run_AMtown02.sh                     # 一键运行指引脚本
├── evo_headless_config.json            # 无显示环境评估配置
│
├── scripts/                            # 脚本
│   ├── extract_ground_truth.py         # 从 bag 提取 RTK 真值
│   ├── evaluate_vo_accuracy.py        # 评估 (ATE/RPE/Completeness)
│   └── update_leaderboard_json.py     # 更新 leaderboard 提交
│
├── submission/                         # Leaderboard 提交
│   ├── ALateFix_leaderboard.json       # 提交文件（含 metrics）
│   └── submission_template.json       # 模板
│
├── Examples/Monocular/                 # 相机配置
│   └── AMtown02_Mono.yaml              # AMtown02 参数
│
├── src/                                # 修改的源码 (ORB-SLAM3)
│   └── System.cc                       # 支持单目全帧轨迹保存
│
├── Examples_old/ROS/ORB_SLAM3/src/     # 修改的 ROS 节点
│   └── ros_mono_compressed.cc          # 保存 CameraTrajectory.txt
│
├── results/                            # 运行结果
│   ├── CameraTrajectory.txt            # 全帧估计轨迹
│   ├── ground_truth.txt                # RTK 地面真值
│   ├── metrics.json                    # 评估指标
│   └── plots/                          # 轨迹图
│       ├── ape_trajectory_map.png      # ATE 轨迹俯视
│       ├── ape_trajectory_raw.png      # ATE 误差曲线
│       ├── rpe_trans_trajectory_*.png  # RPE 平移
│       └── rpe_rot_trajectory_*.png    # RPE 旋转
│
└── docs/                               # 详细文档
    └── LEADERBOARD.md                  # Leaderboard 提交指南
```

---

## 🚀 快速开始

### 环境要求

- ROS Noetic
- ORB-SLAM3（需先编译完整项目）
- evo (`pip install evo`)
- MARS-LVIG AMtown02 bag

### 1. 下载数据集

从 [MARS-LVIG AMtown02](https://drive.google.com/file/d/1rU-1B_B6KJ3dEP6DUooFF3pgMNEOEkcW/view) 下载，放入 `data/AMtown02.bag`。

### 2. 提取 Ground Truth

```bash
source /opt/ros/noetic/setup.bash
python3 scripts/extract_ground_truth.py data/AMtown02.bag -o ground_truth.txt
```

### 3. 运行 ORB-SLAM3

```bash
# 终端 1
roscore

# 终端 2
./Examples_old/ROS/ORB_SLAM3/Mono_Compressed Vocabulary/ORBvoc.txt Examples/Monocular/AMtown02_Mono.yaml

# 终端 3
rosbag play --pause data/AMtown02.bag /left_camera/image/compressed:=/camera/image_raw/compressed
```

ORB-SLAM3 就绪后按**空格**开始播放，Ctrl+C 结束会生成 `CameraTrajectory.txt`。

### 4. 评估

```bash
python3 scripts/evaluate_vo_accuracy.py \
    --groundtruth ground_truth.txt \
    --estimated CameraTrajectory.txt \
    --workdir evaluation_results \
    --json-out evaluation_results/metrics.json

python3 scripts/update_leaderboard_json.py
```

> 评估会生成 `evaluation_results/` 和轨迹图。本仓库 `results/` 目录为预运行结果，供参考。

---

## 📊 评估结果

| 指标 | 数值 |
|------|------|
| ATE RMSE | 6.71 m |
| RPE Trans Drift | 1.34 m/m |
| RPE Rot Drift | 40.65 deg/100m |
| Completeness | 92.91 % |

轨迹图见 `results/plots/`。

---

## 📝 代码修改说明

课程要求使用**全帧轨迹** (CameraTrajectory.txt) 进行评估：

1. **src/System.cc**：移除单目模式下 `SaveTrajectoryTUM` 的限制
2. **ros_mono_compressed.cc**：在 `Shutdown()` 后调用 `SaveTrajectoryTUM("CameraTrajectory.txt")`

将 `src/` 和 `Examples_old/` 下的文件覆盖到 ORB-SLAM3 对应路径后重新编译。

---

## 📤 Leaderboard 提交

提交文件：`submission/ALateFix_leaderboard.json`  
详细说明见 [docs/LEADERBOARD.md](docs/LEADERBOARD.md)。

---

## ⚙️ 配置

- **RTK 话题**: `/dji_osdk_ros/rtk_position`
- **相机话题**: `/left_camera/image/compressed` (remap 到 `/camera/image_raw/compressed`)
- **相机参数**: 沿用 HKisland 配置
