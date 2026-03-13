#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AAE5303 Leaderboard evaluation script.

Computes ATE RMSE, RPE translation drift, RPE rotation drift, and Completeness
using fixed course params: t_max_diff=0.1s, delta=10m, Sim(3) align + scale correction.

Usage:
    python scripts/evaluate_vo_accuracy.py \
        --groundtruth ground_truth.txt \
        --estimated CameraTrajectory.txt \
        --t-max-diff 0.1 \
        --delta-m 10 \
        --workdir evaluation_results \
        --json-out evaluation_results/metrics.json
"""

import argparse
import json
import os
import subprocess
import sys


# Headless: evo needs agg backend via config
EVO_HEADLESS_CONFIG = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "evo_headless_config.json"))


def _run_evo(cmd, save_plot):
    """Run evo command; use config for agg backend in headless env."""
    if save_plot and os.path.exists(EVO_HEADLESS_CONFIG):
        cmd = cmd + ["-c", EVO_HEADLESS_CONFIG]
    return subprocess.run(cmd, capture_output=True, text=True)


def run_evo_ape(gt_path, est_path, t_max_diff, workdir, save_plot=True):
    """Run evo_ape to get ATE RMSE, optionally save trajectory plots."""
    cmd = [
        "evo_ape", "tum", gt_path, est_path,
        "--align", "--correct_scale",
        "--t_max_diff", str(t_max_diff),
        "-va", "--save_results", os.path.join(workdir, "ape.zip")
    ]
    if save_plot:
        cmd.extend(["--save_plot", os.path.join(workdir, "ape_trajectory.png"), "--plot_mode", "xyz"])
    result = _run_evo(cmd, save_plot)
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        return None, result.stderr

    # Parse rmse (evo output format: "      rmse	2.006944")
    for line in result.stdout.split("\n"):
        if "rmse" in line.lower():
            parts = line.split()
            for i, p in enumerate(parts):
                if "rmse" in p.lower() and i + 1 < len(parts):
                    try:
                        return float(parts[i + 1]), None
                    except (ValueError, IndexError):
                        pass
    return None, "Could not parse ATE rmse"


def run_evo_rpe_trans(gt_path, est_path, t_max_diff, delta_m, workdir, save_plot=True):
    """Run evo_rpe for RPE translation (m); divide by delta for m/m."""
    cmd = [
        "evo_rpe", "tum", gt_path, est_path,
        "--align", "--correct_scale",
        "--t_max_diff", str(t_max_diff),
        "--delta", str(delta_m), "--delta_unit", "m",
        "--pose_relation", "trans_part",
        "-va", "--save_results", os.path.join(workdir, "rpe_trans.zip")
    ]
    if save_plot:
        cmd.extend(["--save_plot", os.path.join(workdir, "rpe_trans_trajectory.png"), "--plot_mode", "xyz"])
    result = _run_evo(cmd, save_plot)
    if result.returncode != 0:
        return None, result.stderr

    for line in result.stdout.split("\n"):
        if "mean" in line.lower():
            parts = line.split()
            for i, p in enumerate(parts):
                if "mean" in p.lower() and i + 1 < len(parts):
                    try:
                        return float(parts[i + 1]), None
                    except (ValueError, IndexError):
                        pass
    return None, "Could not parse RPE trans mean"


def run_evo_rpe_rot(gt_path, est_path, t_max_diff, delta_m, workdir, save_plot=True):
    """Run evo_rpe for RPE rotation (deg); (mean/10)*100 for deg/100m."""
    cmd = [
        "evo_rpe", "tum", gt_path, est_path,
        "--align", "--correct_scale",
        "--t_max_diff", str(t_max_diff),
        "--delta", str(delta_m), "--delta_unit", "m",
        "--pose_relation", "angle_deg",
        "-va", "--save_results", os.path.join(workdir, "rpe_rot.zip")
    ]
    if save_plot:
        cmd.extend(["--save_plot", os.path.join(workdir, "rpe_rot_trajectory.png"), "--plot_mode", "xyz"])
    result = _run_evo(cmd, save_plot)
    if result.returncode != 0:
        return None, result.stderr

    for line in result.stdout.split("\n"):
        if "mean" in line.lower():
            try:
                parts = line.split()
                for i, p in enumerate(parts):
                    if "mean" in p.lower() and i + 1 < len(parts):
                        return float(parts[i + 1]), None
            except (ValueError, IndexError):
                pass
        if line.strip().startswith("mean"):
            try:
                return float(line.split()[1]), None
            except (ValueError, IndexError):
                pass
    return None, "Could not parse RPE rot mean"


def get_completeness(gt_path, est_path, t_max_diff):
    """Parse matched from evo_ape output; completeness = matched / gt_count."""
    import re
    with open(gt_path) as f:
        gt_count = sum(1 for line in f if line.strip() and not line.startswith("#"))
    if gt_count == 0:
        return 0.0, None

    cmd = [
        "evo_ape", "tum", gt_path, est_path,
        "--align", "--correct_scale",
        "--t_max_diff", str(t_max_diff),
        "-va"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    for line in result.stdout.split("\n"):
        # Format: "Found 532 of max. 546 possible matching timestamps" -> matched=532
        m = re.search(r"Found\s+(\d+)\s+of\s+max\.\s+\d+", line, re.I)
        if m:
            matched = int(m.group(1))
            return (matched / gt_count * 100.0), None
    return None, "Could not parse completeness"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--groundtruth", "-g", required=True, help="ground truth TUM file")
    parser.add_argument("--estimated", "-e", required=True, help="estimated trajectory (CameraTrajectory.txt)")
    parser.add_argument("--t-max-diff", type=float, default=0.1, help="max timestamp diff (s)")
    parser.add_argument("--delta-m", type=float, default=10.0, help="RPE distance interval (m)")
    parser.add_argument("--workdir", default="evaluation_results", help="output directory")
    parser.add_argument("--json-out", help="output metrics JSON path")
    parser.add_argument("--no-plot", action="store_true", help="do not generate trajectory plots")
    args = parser.parse_args()

    save_plot = not args.no_plot

    os.makedirs(args.workdir, exist_ok=True)

    ate_rmse, err = run_evo_ape(args.groundtruth, args.estimated, args.t_max_diff, args.workdir, save_plot)
    if err:
        print(f"ATE error: {err}", file=sys.stderr)
        ate_rmse = float("nan")

    rpe_trans_mean, err = run_evo_rpe_trans(
        args.groundtruth, args.estimated, args.t_max_diff, args.delta_m, args.workdir, save_plot
    )
    if err or rpe_trans_mean is None:
        if err:
            print(f"RPE trans error: {err}", file=sys.stderr)
        rpe_trans_drift = float("nan")
    else:
        rpe_trans_drift = rpe_trans_mean / args.delta_m  # m/m

    rpe_rot_mean, err = run_evo_rpe_rot(
        args.groundtruth, args.estimated, args.t_max_diff, args.delta_m, args.workdir, save_plot
    )
    if err or rpe_rot_mean is None:
        if err:
            print(f"RPE rot error: {err}", file=sys.stderr)
        rpe_rot_drift = float("nan")
    else:
        rpe_rot_drift = (rpe_rot_mean / args.delta_m) * 100.0  # deg/100m

    completeness, _ = get_completeness(args.groundtruth, args.estimated, args.t_max_diff)
    if completeness is None:
        completeness = float("nan")

    def _round_or_none(val, prec):
        if val is None or (isinstance(val, float) and val != val):  # nan check
            return None
        return round(val, prec)

    metrics = {
        "ate_rmse_m": _round_or_none(ate_rmse, 4),
        "rpe_trans_drift_m_per_m": _round_or_none(rpe_trans_drift, 5),
        "rpe_rot_drift_deg_per_100m": _round_or_none(rpe_rot_drift, 5),
        "completeness_pct": _round_or_none(completeness, 2),
    }

    print("\n========== Evaluation Results ==========")
    for k, v in metrics.items():
        print(f"  {k}: {v}")

    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2, ensure_ascii=False)
        print(f"\nSaved to {args.json_out}")


if __name__ == "__main__":
    main()
