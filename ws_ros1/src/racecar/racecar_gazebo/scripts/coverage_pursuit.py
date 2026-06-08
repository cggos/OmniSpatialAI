#!/usr/bin/env python3
"""
Pure-pursuit path follower for boustrophedon coverage mode.

Subscribes to the coverage path published by coverage_planner.py on
/move_base/TebLocalPlannerROS/global_plan and drives the racecar via
/vesc/low_level/ackermann_cmd_mux/input/navigation.

Improvements over path_pursuit.py:
  - Attributes initialised before subscribers (no race at startup)
  - Numpy-vectorised distance computation (handles large coverage paths)
  - Lookahead cone widened to 90° (path_pursuit uses 45°, which causes
    the robot to stall at row-transition points where the next sweep row
    is perpendicular to the current heading)
  - Division-by-zero guard for diff_angle ≈ 0
  - reach_goal reset when a new path arrives
"""

import math
import rospy
import numpy as np
from numpy import linalg as LA
from tf.transformations import euler_from_quaternion
from nav_msgs.msg import Path, Odometry
from ackermann_msgs.msg import AckermannDriveStamped


class CoveragePursuit:
    def __init__(self):
        self.path_info       = []
        self.Goal            = []
        self.Pose            = []
        self.reach_goal      = False
        self.low_speed_mode  = False
        self.MAX_VELOCITY    = rospy.get_param('~max_velocity',    0.5)
        self.MIN_VELOCITY    = rospy.get_param('~min_velocity',    0.0)
        self.max_angle       = rospy.get_param('~max_angle',       1.0)
        self.steer_velocity  = rospy.get_param('~steer_velocity',  1.0)
        self.LOOKAHEAD       = rospy.get_param('~lookahead',       0.4)

        self._pub = rospy.Publisher(
            '/vesc/low_level/ackermann_cmd_mux/input/navigation',
            AckermannDriveStamped, queue_size=1)

        self._path_sub = rospy.Subscriber(
            '/move_base/TebLocalPlannerROS/global_plan',
            Path, self._path_cb, queue_size=1)
        self._odom_sub = rospy.Subscriber(
            '/pf/pose/odom',
            Odometry, self._odom_cb, queue_size=1)

    # ------------------------------------------------------------------

    def _path_cb(self, msg):
        if not msg.poses:
            return
        self.reach_goal = False
        info = []
        for p in msg.poses:
            q   = (p.pose.orientation.x, p.pose.orientation.y,
                   p.pose.orientation.z, p.pose.orientation.w)
            yaw = euler_from_quaternion(q)[2]
            info.append([float(p.pose.position.x),
                         float(p.pose.position.y),
                         float(yaw)])
        self.path_info = info
        self.Goal      = list(info[-1])
        rospy.loginfo_once("CoveragePursuit: received path with %d points", len(info))

    # ------------------------------------------------------------------

    def _odom_cb(self, msg):
        if self.reach_goal:
            self._publish_stop()
            return

        if not self.path_info:
            self._publish_stop()
            return

        # Vectorised distance to all path points
        path_arr = np.array(self.path_info)   # (N, 3)
        px, py, pw = path_arr[:, 0], path_arr[:, 1], path_arr[:, 2]

        x   = msg.pose.pose.position.x
        y   = msg.pose.pose.position.y
        q   = (msg.pose.pose.orientation.x, msg.pose.pose.orientation.y,
               msg.pose.pose.orientation.z, msg.pose.pose.orientation.w)
        yaw = euler_from_quaternion(q)[2]
        self.Pose = [x, y, yaw]

        # Goal proximity
        d_goal = math.hypot(self.Goal[0] - x, self.Goal[1] - y)
        if d_goal < 1.0:
            self.low_speed_mode = True
            if d_goal < 0.3:
                self.reach_goal = True
                rospy.loginfo("CoveragePursuit: goal reached!")
                self._publish_stop()
                return
        else:
            self.low_speed_mode = False

        dist_arr = np.sqrt((px - x) ** 2 + (py - y) ** 2)

        # Default: closest point
        goal_idx = int(np.argmin(dist_arr))

        # Look for a point ~LOOKAHEAD ahead and within 90° of heading
        band = np.where(
            (dist_arr < self.LOOKAHEAD + 0.3) &
            (dist_arr > self.LOOKAHEAD - 0.3)
        )[0]
        for idx in band:
            v1 = [px[idx] - x, py[idx] - y]
            v2 = [math.cos(yaw), math.sin(yaw)]
            if abs(self._angle(v1, v2)) < math.pi / 2:
                goal_idx = idx
                break

        L          = float(dist_arr[goal_idx])
        diff_angle = float(pw[goal_idx]) - yaw

        if abs(math.sin(diff_angle)) < 1e-6:
            steer = 0.0
        else:
            r     = L / (2.0 * math.sin(diff_angle))
            steer = 2.0 * math.atan(0.4 / r)

        steer = float(np.clip(steer, -self.max_angle, self.max_angle))
        steer = 0.0 if abs(steer) < 0.1 else steer

        if self.low_speed_mode:
            speed = 0.5
        else:
            k     = (self.MIN_VELOCITY - self.MAX_VELOCITY) / self.max_angle + 0.5
            speed = k * abs(steer) + self.MAX_VELOCITY

        cmd = AckermannDriveStamped()
        cmd.drive.speed                   = speed
        cmd.drive.steering_angle          = steer
        cmd.drive.steering_angle_velocity = self.steer_velocity
        self._pub.publish(cmd)

    # ------------------------------------------------------------------

    def _publish_stop(self):
        self._pub.publish(AckermannDriveStamped())

    @staticmethod
    def _angle(v1, v2):
        cos_a = np.dot(v1, v2)
        sin_a = LA.norm(np.cross(v1, v2))
        return np.arctan2(sin_a, cos_a)


if __name__ == '__main__':
    rospy.init_node('coverage_pursuit')
    CoveragePursuit()
    rospy.spin()
