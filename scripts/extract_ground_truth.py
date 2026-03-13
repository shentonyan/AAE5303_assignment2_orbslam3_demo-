#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract RTK ground truth from MARS-LVIG rosbag and convert to TUM format.

RTK topic: /dji_osdk_ros/rtk_position (sensor_msgs/NavSatFix)
Output format: TUM (t tx ty tz qx qy qz qw), timestamp in seconds, position in local ENU.

Usage:
    python scripts/extract_ground_truth.py data/AMtown02.bag -o ground_truth.txt
"""

import argparse
import sys

try:
    import rosbag
except ImportError:
    print("Error: rosbag required. Source ROS first: source /opt/ros/noetic/setup.bash")
    sys.exit(1)

import numpy as np


def geodetic_to_enu_simple(lat, lon, alt, lat0, lon0, alt0):
    """
    Simplified WGS84 to local ENU conversion (for small areas, e.g. UAV trajectory).
    Uses planar approximation, sufficient for trajectories within a few km.
    """
    R = 6378137.0  # WGS84 semi-major axis (m)
    lat_rad = np.radians(lat)
    lon_rad = np.radians(lon)
    lat0_rad = np.radians(lat0)
    lon0_rad = np.radians(lon0)

    # Local ENU: East = x, North = y, Up = z
    x = R * (lon_rad - lon0_rad) * np.cos(lat0_rad)
    y = R * (lat_rad - lat0_rad)
    z = alt - alt0
    return x, y, z


def extract_rtk_from_bag(bag_path, topic="/dji_osdk_ros/rtk_position", output_path="ground_truth.txt"):
    """
    Extract RTK poses from bag and save as TUM format.
    RTK provides position only; orientation uses identity quaternion (0,0,0,1).
    """
    print(f"Reading: {bag_path}")
    print(f"RTK topic: {topic}")

    bag = rosbag.Bag(bag_path)
    rtk_data = []

    try:
        for _, msg, _ in bag.read_messages(topics=[topic]):
            timestamp = msg.header.stamp.to_sec()
            lat = msg.latitude
            lon = msg.longitude
            alt = msg.altitude
            rtk_data.append([timestamp, lat, lon, alt])
    finally:
        bag.close()

    if not rtk_data:
        print(f"Error: No data found on topic {topic}. Check your bag file.")
        sys.exit(1)

    rtk_data = np.array(rtk_data)
    lat0, lon0, alt0 = rtk_data[0, 1], rtk_data[0, 2], rtk_data[0, 3]

    # Convert to local ENU
    x, y, z = geodetic_to_enu_simple(
        rtk_data[:, 1], rtk_data[:, 2], rtk_data[:, 3],
        lat0, lon0, alt0
    )

    # Write TUM format: t tx ty tz qx qy qz qw (identity quaternion for orientation)
    with open(output_path, "w") as f:
        for i in range(len(rtk_data)):
            f.write(f"{rtk_data[i, 0]:.6f} {x[i]:.9f} {y[i]:.9f} {z[i]:.9f} 0 0 0 1\n")

    print(f"Saved {len(rtk_data)} poses to {output_path}")
    return len(rtk_data)


def main():
    parser = argparse.ArgumentParser(description="Extract RTK ground truth from MARS-LVIG bag")
    parser.add_argument("bag", help="rosbag file path")
    parser.add_argument("-o", "--output", default="ground_truth.txt", help="output file path")
    parser.add_argument("-t", "--topic", default="/dji_osdk_ros/rtk_position",
                        help="RTK topic (default: /dji_osdk_ros/rtk_position)")
    args = parser.parse_args()

    extract_rtk_from_bag(args.bag, topic=args.topic, output_path=args.output)


if __name__ == "__main__":
    main()
