"""Read nav_msgs/msg/Odometry and sensor_msgs/msg/Image from a ROS2 bag (rosbag2).

Usage:
  python ros2bag_read.py --bag-path /path/to/bag --storage-id sqlite3 \
      --topics /tf,/camera/image_raw --save-images out_dir

This script uses rosbag2_py SequentialReader and rclpy.serialization.deserialize_message
to read messages. If cv_bridge is installed it will convert Image messages to OpenCV
images (numpy) and can save them as PNG files.
"""

from __future__ import annotations

import argparse
import importlib
import os
import sys
from typing import Dict, List, Optional, Tuple
import math
import numpy as np
import tf_transformations as transform_mod

fo = open(
    "/tmp/odom_output.tum",
    "w",
)


def try_import(name: str):
    try:
        return importlib.import_module(name)
    except Exception:
        return None


rosbag2_py = try_import("rosbag2_py")
rclpy_serialization = try_import("rclpy.serialization")
cv_bridge_mod = try_import("cv_bridge")
cv2 = try_import("cv2")


def get_msg_class_from_type(type_str: str):
    """Given a ROS type string like 'nav_msgs/msg/Odometry', import and return the message class."""
    # type_str expected: 'package/msg/MessageName'
    if "/msg/" in type_str:
        pkg, _, msg = type_str.partition("/msg/")
        module_name = f"{pkg}.msg"
        try:
            module = importlib.import_module(module_name)
            return getattr(module, msg)
        except Exception:
            return None
    return None


def read_ros2_bag(
    bag_path: str,
    storage_id: str = "sqlite3",
    topics: Optional[List[str]] = None,
    save_images_dir: Optional[str] = None,
    max_msgs: Optional[int] = None,
):
    """Read messages from a ros2 bag.

    Args:
        bag_path: path to the bag (directory or file depending on storage)
        storage_id: storage plugin id (e.g. sqlite3, etc.)
        topics: list of topic names to filter (None = all)
        save_images_dir: if provided, save Image messages to this directory
        max_msgs: optional maximum number of messages to read (total)
    """
    if rosbag2_py is None:
        raise RuntimeError(
            "rosbag2_py not available. Run in a ROS2 Python environment (install rosbag2_py)."
        )
    if rclpy_serialization is None:
        raise RuntimeError(
            "rclpy.serialization not available. Run in a ROS2 Python environment (install rclpy)."
        )

    from rosbag2_py import SequentialReader, StorageOptions, ConverterOptions
    from rclpy.serialization import deserialize_message

    storage_options = StorageOptions(uri=bag_path, storage_id=storage_id)
    # Use CDR by default for serialization formats
    converter_options = ConverterOptions(
        input_serialization_format="cdr", output_serialization_format="cdr"
    )

    reader = SequentialReader()
    reader.open(storage_options, converter_options)

    topics_and_types = reader.get_all_topics_and_types()
    # topics_and_types is a list of TopicMetadata-like objects with name and type
    topic_type_map: Dict[str, str] = {t.name: t.type for t in topics_and_types}

    # Optionally print topics
    print("Topics in bag:")
    for name, t in topic_type_map.items():
        print(f"  {name}: {t}")

    # Build a cache of message classes per topic
    msg_class_cache: Dict[str, object] = {}
    for tn, tt in topic_type_map.items():
        cls = get_msg_class_from_type(tt)
        if cls is not None:
            msg_class_cache[tn] = cls

    bridge = None
    if cv_bridge_mod is not None:
        try:
            from cv_bridge import CvBridge

            bridge = CvBridge()
        except Exception:
            bridge = None

    if transform_mod is not None:
        print("Using transform module:", transform_mod.__name__)

    if save_images_dir:
        os.makedirs(save_images_dir, exist_ok=True)

    count = 0
    # storage for first/last odometry per topic when computing deltas
    odom_first: Dict[
        str, Tuple[Tuple[float, float, float], Tuple[float, float, float, float], int]
    ] = {}
    odom_last: Dict[
        str, Tuple[Tuple[float, float, float], Tuple[float, float, float, float], int]
    ] = {}

    # If topics filter provided, make a set
    topics_filter = set(topics) if topics else None

    is_odom_init = False
    odom_first = None
    odom_last = None

    # Read loop
    while reader.has_next():
        (topic, data, t) = reader.read_next()
        if topics_filter and topic not in topics_filter:
            continue

        if topic not in topic_type_map:
            # Unknown topic type, skip
            continue

        type_str = topic_type_map[topic]
        msg_cls = msg_class_cache.get(topic)
        if msg_cls is None:
            # try to import on the fly
            msg_cls = get_msg_class_from_type(type_str)
            if msg_cls:
                msg_class_cache[topic] = msg_cls

        try:
            msg = deserialize_message(data, msg_cls) if msg_cls is not None else None
        except Exception as e:
            print(f"Failed to deserialize message on {topic}: {e}")
            msg = None

        pose = None

        if type_str == "nav_msgs/msg/Odometry":
            if msg is not None:
                pose = msg.pose.pose
        elif type_str == "geometry_msgs/msg/PoseStamped":
            if msg is not None:
                pose = msg.pose
        elif type_str == "sensor_msgs/msg/Image":
            print(f"[{t}] Image on {topic}")
            if msg is not None:
                if bridge is not None and cv2 is not None:
                    try:
                        cv_img = bridge.imgmsg_to_cv2(
                            msg, desired_encoding=msg.encoding
                        )
                    except Exception:
                        # fallback to 'passthrough' or 'bgr8'
                        try:
                            cv_img = bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
                        except Exception as e:
                            print(f"  cv_bridge conversion failed: {e}")
                            cv_img = None

                    if cv_img is not None:
                        print(f"  image size: {cv_img.shape}")
                        if save_images_dir:
                            fname = os.path.join(
                                save_images_dir,
                                f"{topic.strip('/').replace('/','_')}_{count:06d}.png",
                            )
                            cv2.imwrite(fname, cv_img)
                            print(f"  saved: {fname}")
                else:
                    # No cv_bridge or opencv: save raw bytes
                    if save_images_dir:
                        fname = os.path.join(
                            save_images_dir,
                            f"{topic.strip('/').replace('/','_')}_{count:06d}.raw",
                        )
                        with open(fname, "wb") as fh:
                            fh.write(msg.data)
                        print(f"  saved raw image data to: {fname}")
        else:
            # other topics: optionally print short summary
            print(f"[{t}] {type_str} on {topic}")

        if pose is not None:
            # store as tuple (position, orientation quaternion)
            pos = (pose.position.x, pose.position.y, pose.position.z)
            ori = (
                pose.orientation.w,
                pose.orientation.x,
                pose.orientation.y,
                pose.orientation.z,
            )

            # Message quaternions are (x,y,z,w) in ROS messages; our original 'ori' variable was (w,x,y,z)
            # Build quaternion in (x,y,z,w) order for the transform lib.
            q_xyzw = (
                pose.orientation.x,
                pose.orientation.y,
                pose.orientation.z,
                pose.orientation.w,
            )

            angle_rad = math.radians(10.0)
            R_given = np.array([[0.0, -1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]])

            if transform_mod is not None:
                Rx9_4 = transform_mod.euler_matrix(0.0, angle_rad, 0.0)
                Rx9 = Rx9_4[:3, :3]

                qmat = transform_mod.quaternion_matrix(q_xyzw)  # 4x4
                Rgiven_4 = np.eye(4)
                Rgiven_4[:3, :3] = R_given

                R_new_4 = Rgiven_4 @ Rx9_4 @ qmat

                # new quaternion from matrix (returns x,y,z,w)
                q_new_xyzw = transform_mod.quaternion_from_matrix(R_new_4)

                # # transform position
                # p_vec = np.array(pos)
                # p_new = (R_given @ Rx9) @ p_vec + np.array([0.0, 0.5, 0.15])
                # pos = (float(p_new[0]), float(p_new[1]), float(p_new[2]))

                # # update ori to (w,x,y,z)
                # ori = (float(q_new_xyzw[3]), float(q_new_xyzw[0]), float(q_new_xyzw[1]), float(q_new_xyzw[2]))
            else:
                raise RuntimeError(
                    "No transform/quaternion library available: install 'tf_transformations' or 'scipy'"
                )
            if not is_odom_init:
                odom_first = (pos, ori, t)
                is_odom_init = True
            odom_last = (pos, ori, t)

            # write transformed pose (time, px, py, pz, qx, qy, qz, qw)
            fo.write(
                ("{} {} {} {} {} {} {} {}\n").format(
                    t * 1e-9,
                    pos[0],
                    pos[1],
                    pos[2],
                    ori[1],
                    ori[2],
                    ori[3],
                    ori[0],
                )
            )

        count += 1
        if max_msgs is not None and count >= max_msgs:
            break

    print(f"Read {count} messages from bag.")

    if odom_first and odom_last:
        compute_odom_delta(odom_first, odom_last)

    fo.close()


def compute_odom_delta(odom_first, odom_last):
    if odom_first is None or odom_last is None:
        print(
            f"insufficient odometry messages (first={odom_first is not None}, last={odom_last is not None})"
        )
        return
    pos1, ori1, ts1 = odom_first
    pos2, ori2, ts2 = odom_last
    dx = pos2[0] - pos1[0]
    dy = pos2[1] - pos1[1]
    dz = pos2[2] - pos1[2]

    # quaternion math: q_rel = q2 * q1^{-1}
    def quat_inv(q):
        w, x, y, z = q
        return (w, -x, -y, -z)

    def quat_mul(a, b):
        aw, ax, ay, az = a
        bw, bx, by, bz = b
        return (
            aw * bw - ax * bx - ay * by - az * bz,
            aw * bx + ax * bw + ay * bz - az * by,
            aw * by - ax * bz + ay * bw + az * bx,
            aw * bz + ax * by - ay * bx + az * bw,
        )

    def quat_to_euler(q):
        # q is (w, x, y, z)
        w, x, y, z = q
        # roll (x-axis rotation)
        sinr_cosp = 2.0 * (w * x + y * z)
        cosr_cosp = 1.0 - 2.0 * (x * x + y * y)
        roll = math.atan2(sinr_cosp, cosr_cosp)

        # pitch (y-axis)
        sinp = 2.0 * (w * y - z * x)
        if abs(sinp) >= 1:
            pitch = math.copysign(math.pi / 2, sinp)
        else:
            pitch = math.asin(sinp)

        # yaw (z-axis)
        siny_cosp = 2.0 * (w * z + x * y)
        cosy_cosp = 1.0 - 2.0 * (y * y + z * z)
        yaw = math.atan2(siny_cosp, cosy_cosp)
        return roll, pitch, yaw

    q1 = ori1
    q2 = ori2
    q_rel = quat_mul(q2, quat_inv(q1))
    # rotation angle (radians)
    w_rel = max(min(q_rel[0], 1.0), -1.0)
    angle = 2.0 * math.acos(w_rel)
    # convert to euler for relative yaw/roll/pitch
    r1, p1, y1 = quat_to_euler(q1)
    r2, p2, y2 = quat_to_euler(q2)
    dr = r2 - r1
    dp = p2 - p1
    dyaw = y2 - y1

    print(f"  time first: {ts1}, time last: {ts2}")
    print(
        f"  position delta: dx={dx:.6f}, dy={dy:.6f}, dz={dz:.6f} (Euclidean={math.sqrt(dx*dx+dy*dy+dz*dz):.6f})"
    )
    print(f"  rotation: angle={angle:.6f} rad ({math.degrees(angle):.3f} deg)")
    print(f"  relative euler delta (r,p,y) = ({dr:.6f}, {dp:.6f}, {dyaw:.6f}) rad")


def parse_args(argv: Optional[List[str]] = None):
    p = argparse.ArgumentParser(
        description="Read selected topics from a ROS2 bag (rosbag2)"
    )
    p.add_argument("--bag-path", required=True, help="Path (uri) to the ros2 bag")
    p.add_argument(
        "--storage-id", default="sqlite3", help="rosbag2 storage id (sqlite3, etc.)"
    )
    p.add_argument(
        "--topics",
        default=None,
        help="Comma-separated list of topics to read (default: all)",
    )
    p.add_argument(
        "--save-images", default=None, help="Directory to save images (optional)"
    )
    p.add_argument(
        "--max-msgs", type=int, default=None, help="Maximum number of messages to read"
    )
    return p.parse_args(argv)


def main(argv: Optional[List[str]] = None):
    args = parse_args(argv)
    topics = args.topics.split(",") if args.topics else None

    read_ros2_bag(
        bag_path=args.bag_path,
        storage_id=args.storage_id,
        topics=topics,
        save_images_dir=args.save_images,
        max_msgs=args.max_msgs,
    )


if __name__ == "__main__":
    main()
