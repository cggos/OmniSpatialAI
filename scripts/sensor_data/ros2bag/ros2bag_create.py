#!/usr/bin/env python3
"""
ros2bag_create.py

ROS2 Python script to create a rosbag2 (sqlite3) file from text/image files.

Usage example:
  python3 ros2bag_create.py --data-root /opt/cgsai/data --bag-path /tmp/sai_ros2 --storage sqlite3

Notes:
- Requires a ROS2 Python environment with: rclpy, rosbag2_py, rclpy.serialization,
  cv_bridge and OpenCV (cv2).
"""

from __future__ import annotations

import argparse
import math
import os
from typing import Tuple

import rclpy
from rclpy.serialization import serialize_message

import rosbag2_py
from rosbag2_py import StorageOptions, ConverterOptions, TopicMetadata
from rosbag2_py import SequentialWriter as Writer

from cv_bridge import CvBridge

import cv2

topic_rtk = "/sensor/rtk"
topic_wheel = "/sensor/wheel"
topic_imu = "/sensor/imu"
topic_img0 = "/camera/img0/image_raw"
topic_img1 = "/camera/img1/image_raw"
topic_color = "/camera/color/image_raw"

t0 = 1731564550.916 + 30 # 30s delay

def ensure_deps():
    if rosbag2_py is None:
        raise RuntimeError(
            "rosbag2_py not available. Run in a ROS2 Python environment with rosbag2_py."
        )
    if rclpy is None:
        raise RuntimeError("rclpy not available. Run in a ROS2 Python environment.")
    if CvBridge is None or cv2 is None:
        print(
            "Warning: cv_bridge or cv2 missing. Image conversion may fail or be limited."
        )


def seconds_to_sec_nsec(total_seconds: float) -> Tuple[int, int]:
    """
    将浮点数表示的秒数转换为 (秒, 纳秒) 的元组。
    Args:
        total_seconds: 浮点数，表示总秒数。
    Returns:
        一个元组，其中包含：
        - sec (int): 整数秒部分。
        - nsec (int): 纳秒部分，范围通常在 [-999_999_999, 999_999_999] 之间。
                      符号与原始浮点数的符号或其小数部分符号一致。
    """
    if not isinstance(total_seconds, (float, int)):
        raise TypeError("输入必须是浮点数或整数。")
    NS_PER_SEC = 1_000_000_000  # 10亿纳秒等于1秒
    # math.modf(x) 返回 (fractional_part, integral_part)
    # 整数部分为浮点数，需要转成int
    # fractional_part 会带有原始数值的符号
    frac_part, sec_float = math.modf(total_seconds)
    sec = int(sec_float)
    # 将小数部分转换为纳秒，并进行四舍五入以处理浮点精度问题
    nsec = round(frac_part * NS_PER_SEC)
    # 处理由于四舍五入可能导致的进位或借位
    # 例如：1.9999999999 秒，小数部分可能四舍五入到 1_000_000_000 纳秒
    # 例如：-1.9999999999 秒，小数部分可能四舍五入到 -1_000_000_000 纳秒
    if nsec == NS_PER_SEC:
        sec += 1
        nsec = 0
    elif nsec == -NS_PER_SEC:
        sec -= 1
        nsec = 0
    return sec, nsec


def make_topics(writer: Writer):
    # Create topics we will write. Use CDR serialization format.
    topics = [
        (topic_imu, "sensor_msgs/msg/Imu"),
        (topic_img0, "sensor_msgs/msg/Image"),
        (topic_img1, "sensor_msgs/msg/Image"),
        (topic_color, "sensor_msgs/msg/Image"),
        (topic_rtk, "novatel_gps_msgs/msg/Inspvax"),
        (topic_wheel, "geometry_msgs/msg/TwistStamped"),
    ]
    for name, type_str in topics:
        tm = TopicMetadata(name=name, type=type_str, serialization_format="cdr")
        writer.create_topic(tm)


def write_rtks(writer: Writer, data_root: str):
    try:
        from novatel_gps_msgs.msg import Inspvax
    except Exception:
        print(
            "novatel_gps_msgs.Inspvax not available: install package or source workspace; skipping RTK"
        )
        return

    fn = os.path.join(data_root, "rtk.txt")
    if not os.path.exists(fn):
        print("--- rtk.txt not found, skipping RTK")
        return
    print("--- RTK (Inspvax) begin")
    with open(fn, "r", encoding="utf-8") as fh:
        count = 0
        for line in fh:
            # if count == 0:
            #   continue
            parts = line.split()
            if len(parts) < 11:
                print(f"RTK short line {count}, skipping")
                continue
            try:
                ins = Inspvax()
                t = float(parts[1])
                if t < t0:
                    continue
                sec, nsec = seconds_to_sec_nsec(t)
                ins.header.stamp.sec = sec
                ins.header.stamp.nanosec = nsec
                ins.ins_status = parts[0]
                ins.latitude = float(parts[2])
                ins.longitude = float(parts[3])
                ins.altitude = float(parts[4])
                ins.latitude_std = float(parts[5])
                ins.longitude_std = float(parts[6])
                ins.altitude_std = float(parts[7])
                ins.east_velocity = float(parts[8])
                ins.north_velocity = float(parts[9])
                ins.up_velocity = float(parts[10])
                # azimuth may or may not be present as parts[11]
                if len(parts) > 11:
                    ins.azimuth = float(parts[11])
                data = serialize_message(ins)
                writer.write(topic_rtk, data, int(round(t * 1e9)))
            except Exception as e:
                print(f"RTK (Inspvax) parse error line {count}: {e}")
            count += 1
    print(f"--- RTK (Inspvax) end (count: {count})")


def write_wheels(writer: Writer, data_root: str):
    from geometry_msgs.msg import TwistStamped

    fn = os.path.join(data_root, "whl.txt")
    if not os.path.exists(fn):
        print("--- whl.txt not found, skipping two wheel")
        return
    print("--- Whl (TwistStamped) begin")
    with open(fn, "r", encoding="utf-8") as fh:
        # # skip first header line as C++ did
        # next(fh, None)
        count = 0
        for line in fh:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            try:
                t = float(parts[0])
                if t < t0:
                    continue
                sec, nsec = seconds_to_sec_nsec(t)
                twist_ts = TwistStamped()  # FLU coordinates
                twist_ts.header.stamp.sec = sec
                twist_ts.header.stamp.nanosec = nsec
                linear_velocity = 0.0
                angular_velocity = 0.0
                if len(parts) == 2:
                    linear_velocity = float(parts[1])
                if len(parts) == 3:
                    left_speed = float(parts[1])
                    right_speed = float(parts[2])
                    wheel_base = 0.465
                    linear_velocity = (right_speed + left_speed) / 2.0
                    angular_velocity = (left_speed - right_speed) / wheel_base
                twist_ts.twist.linear.x = linear_velocity
                twist_ts.twist.linear.y = 0.0
                twist_ts.twist.linear.z = 0.0
                twist_ts.twist.angular.z = angular_velocity
                data = serialize_message(twist_ts)
                writer.write(topic_wheel, data, int(round(t * 1e9)))
            except Exception as e:
                print(f"Whl (TwistStamped) parse error: {e}")
            count += 1
    print(f"--- Whl (TwistStamped) end (count: {count})")


def write_wheel_speed(writer: Writer, data_root: str):
    from std_msgs.msg import String

    fn = os.path.join(data_root, "whl.txt")
    if not os.path.exists(fn):
        print("--- whl.txt not found, skipping wheel speed")
        return
    print("--- Whl (String) begin")
    with open(fn, "r", encoding="utf-8") as fh:
        count = 0
        for line in fh:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            try:
                t = float(parts[0])
                msg = String()
                msg.data = line
                data = serialize_message(msg)
                writer.write("/sensor/wheelspeed", data, int(round(t * 1e9)))
            except Exception as e:
                print(f"Whl (String) parse error: {e}")
            count += 1
    print(f"--- Whl (String) end (count: {count})")


def write_imus(writer: Writer, data_root: str):
    from sensor_msgs.msg import Imu

    fn = os.path.join(data_root, "imu.txt")
    if not os.path.exists(fn):
        print("--- IMU file not found, skipping:", fn)
        return
    print("--- IMU begin")
    with open(fn, "r", encoding="utf-8") as fh:
        count = 0
        for line in fh:
            # if count == 0:
            #   # skip header line like in C++ version
            #   continue
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            try:
                t = float(parts[0])
                if t < t0:
                    continue
                imu = Imu()
                sec, nsec = seconds_to_sec_nsec(t)
                imu.header.stamp.sec = sec
                imu.header.stamp.nanosec = nsec
                # linear_acc x,y,z then ang vel x,y,z
                imu.linear_acceleration.x = float(parts[1])
                imu.linear_acceleration.y = float(parts[2])
                imu.linear_acceleration.z = float(parts[3])
                imu.angular_velocity.x = float(parts[4])
                imu.angular_velocity.y = float(parts[5])
                imu.angular_velocity.z = float(parts[6])

                data = serialize_message(imu)
                writer.write(topic_imu, data, int(round(t * 1e9)))
            except Exception as e:
                print(f"IMU parse error line {count}: {e}")
            count += 1
    print(f"--- IMU end (count: {count})")


def write_imgs(writer: Writer, data_root: str):
    from sensor_msgs.msg import Image

    bridge = CvBridge() if CvBridge is not None else None

    fn = os.path.join(data_root, "img.txt")
    if not os.path.exists(fn):
        print("--- img.txt not found, skipping stereo imgs")
        return
    print("--- Stereo IMGs begin")
    with open(fn, "r", encoding="utf-8") as fh:
        count = 0
        for line in fh:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            t = float(parts[0])
            tag = format(t, ".3f")
            if t < t0:
                continue
            lfn = os.path.join(data_root, f"{tag}000_l.png")  # TODO: use tag from file
            rfn = os.path.join(data_root, f"{tag}000_r.png")
            if os.path.exists(lfn):
                img_l = cv2.imread(lfn, cv2.IMREAD_UNCHANGED)
            else:
                img_l = None
                print(f"Stereo: left not found for {tag}")
            if os.path.exists(rfn):
                img_r = cv2.imread(rfn, cv2.IMREAD_UNCHANGED)
            else:
                img_r = None
                print(f"Stereo: right not found for {tag}")

            try:
                if img_l is not None and img_l.size != 0:
                    # ensure mono8
                    if len(img_l.shape) == 3:
                        img_l = cv2.cvtColor(img_l, cv2.COLOR_BGR2GRAY)
                    if bridge is not None:
                        ros_img = bridge.cv2_to_imgmsg(img_l, encoding="mono8")
                    else:
                        # fallback: construct msg manually
                        from sensor_msgs.msg import Image as ImageMsg

                        ros_img = ImageMsg()
                        ros_img.height = img_l.shape[0]
                        ros_img.width = img_l.shape[1]
                        ros_img.encoding = "mono8"
                        ros_img.step = ros_img.width
                        ros_img.data = img_l.tobytes()

                    sec, nsec = seconds_to_sec_nsec(t)
                    ros_img.header.stamp.sec = sec
                    ros_img.header.stamp.nanosec = nsec
                    ros_img.header.frame_id = "image"
                    data = serialize_message(ros_img)
                    writer.write(topic_img0, data, int(round(t * 1e9)))
                if img_r is not None and img_r.size != 0:
                    if len(img_r.shape) == 3:
                        img_r = cv2.cvtColor(img_r, cv2.COLOR_BGR2GRAY)
                    if bridge is not None:
                        ros_img = bridge.cv2_to_imgmsg(img_r, encoding="mono8")
                    else:
                        from sensor_msgs.msg import Image as ImageMsg

                        ros_img = ImageMsg()
                        ros_img.height = img_r.shape[0]
                        ros_img.width = img_r.shape[1]
                        ros_img.encoding = "mono8"
                        ros_img.step = ros_img.width
                        ros_img.data = img_r.tobytes()
                    sec, nsec = seconds_to_sec_nsec(t)
                    ros_img.header.stamp.sec = sec
                    ros_img.header.stamp.nanosec = nsec
                    ros_img.header.frame_id = "image"
                    data = serialize_message(ros_img)
                    writer.write(topic_img1, data, int(round(t * 1e9)))
            except Exception as e:
                print(f"Stereo image write error for {tag}: {e}")
            count += 1
    print(f"--- Stereo IMGs end (count: {count})")


def write_color_imgs(writer: Writer, data_root: str):
    bridge = CvBridge() if CvBridge is not None else None
    fn = os.path.join(data_root, "img_c.txt")
    if not os.path.exists(fn):
        print("--- img_c.txt not found, skipping color imgs")
        return
    print("--- Color IMG begin")
    with open(fn, "r", encoding="utf-8") as fh:
        count = 0
        for line in fh:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            t = float(parts[0])
            tag = str(t)
            cfn = os.path.join(data_root, f"{tag}_c.png")
            if not os.path.exists(cfn):
                print(f"color img not found for {tag}")
                continue
            img = cv2.imread(cfn, cv2.IMREAD_COLOR)
            if img is None or img.size == 0:
                print(f"color read failed for {tag}")
                continue
            if img.shape[2] != 3:
                print(f"count {count}: img_c channels != 3")
                continue
            try:
                if bridge is not None:
                    ros_img = bridge.cv2_to_imgmsg(img, encoding="bgr8")
                else:
                    from sensor_msgs.msg import Image as ImageMsg

                    ros_img = ImageMsg()
                    ros_img.height = img.shape[0]
                    ros_img.width = img.shape[1]
                    ros_img.encoding = "bgr8"
                    ros_img.step = img.shape[1] * 3
                    ros_img.data = img.tobytes()
                sec, nsec = seconds_to_sec_nsec(t)
                ros_img.header.stamp.sec = sec
                ros_img.header.stamp.nanosec = nsec
                ros_img.header.frame_id = "image"
                data = serialize_message(ros_img)
                writer.write(topic_color, data, int(round(t * 1e9)))
            except Exception as e:
                print(f"color image write error for {tag}: {e}")
            count += 1
    print(f"--- Color IMG end (count: {count})")


def main():
    parser = argparse.ArgumentParser(
        description="Create ROS2 bag from dataset text files"
    )
    parser.add_argument(
        "--data-root",
        default="/opt/cgsai/data/",
        help="Root directory where imu.txt, img.txt, etc. live",
    )
    parser.add_argument(
        "--bag-path",
        default="/tmp/sai_ros2bag",
        help="Directory/uri for rosbag2 output",
    )
    parser.add_argument(
        "--storage", default="sqlite3", help="rosbag2 storage id (sqlite3, etc.)"
    )
    args = parser.parse_args()

    data_root = args.data_root
    if not data_root.endswith("/"):
        data_root += "/"

    ensure_deps()

    # Prepare writer
    storage_options = StorageOptions(uri=args.bag_path, storage_id=args.storage)
    converter_options = ConverterOptions(
        input_serialization_format="cdr", output_serialization_format="cdr"
    )

    writer = Writer()
    writer.open(storage_options, converter_options)
    make_topics(writer)

    print("Bag open, writing to:", args.bag_path)

    # Write data
    write_rtks(writer, data_root)
    write_wheels(writer, data_root)
    # write_wheel_speed(writer, data_root)
    write_imus(writer, data_root)
    write_imgs(writer, data_root)
    write_color_imgs(writer, data_root)

    print("Bag creation finished.")


if __name__ == "__main__":
    main()
