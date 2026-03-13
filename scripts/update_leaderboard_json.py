#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Update leaderboard submission JSON from evaluation_results/metrics.json.
"""

import argparse
import json
import os

GROUP_NAME = "ALateFix"
REPO_URL = "https://github.com/shentonyan/AAE5303_assignment2_orbslam.git"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--metrics", default="evaluation_results/metrics.json",
                        help="path to metrics JSON")
    parser.add_argument("--output", default="submission/ALateFix_leaderboard.json",
                        help="output leaderboard JSON path")
    args = parser.parse_args()

    if not os.path.exists(args.metrics):
        print(f"Error: {args.metrics} not found. Run evaluation first.")
        return 1

    with open(args.metrics, encoding="utf-8") as f:
        metrics = json.load(f)

    submission = {
        "group_name": GROUP_NAME,
        "project_private_repo_url": REPO_URL,
        "metrics": {
            "ate_rmse_m": metrics.get("ate_rmse_m", 0),
            "rpe_trans_drift_m_per_m": metrics.get("rpe_trans_drift_m_per_m", 0),
            "rpe_rot_drift_deg_per_100m": metrics.get("rpe_rot_drift_deg_per_100m", 0),
            "completeness_pct": metrics.get("completeness_pct", 0),
        }
    }

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(submission, f, indent=2, ensure_ascii=False)

    print(f"Updated {args.output}")
    return 0


if __name__ == "__main__":
    exit(main())
