#!/usr/bin/env python3

'''
Odometry node that publishes odom→base_link TF (and /vesc/odom) from
Gazebo ground truth.  Identical to gazebo_odometry.py except that
header.frame_id is 'odom' instead of 'map', so the TF tree becomes

    map → odom → base_link

where AMCL is responsible for the map→odom transform.
'''

import rospy
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Pose, Twist, Transform, TransformStamped
from gazebo_msgs.msg import LinkStates
from std_msgs.msg import Header
import numpy as np
import math
import tf2_ros


class OdometryNode:
    pub_odom = rospy.Publisher('/odom_fusion', Odometry, queue_size=1)

    def __init__(self):
        self.last_received_pose  = Pose()
        self.last_received_twist = Twist()
        self.last_recieved_stamp = None

        rospy.Timer(rospy.Duration(.05), self.timer_callback)  # 20 Hz

        self.tf_pub = tf2_ros.TransformBroadcaster()

        rospy.Subscriber('/gazebo/link_states', LinkStates,
                         self.sub_robot_pose_update)

    def sub_robot_pose_update(self, msg):
        try:
            arrayIndex = msg.name.index('racecar::base_link')
        except ValueError:
            pass
        else:
            self.last_received_pose  = msg.pose[arrayIndex]
            self.last_received_twist = msg.twist[arrayIndex]
        self.last_recieved_stamp = rospy.Time.now()

    def timer_callback(self, event):
        if self.last_recieved_stamp is None:
            return

        cmd = Odometry()
        cmd.header.stamp    = self.last_recieved_stamp
        cmd.header.frame_id = 'odom'       # ← 'odom' not 'map'
        cmd.child_frame_id  = 'base_link'
        cmd.pose.pose       = self.last_received_pose
        cmd.twist.twist     = self.last_received_twist
        self.pub_odom.publish(cmd)

        tf = TransformStamped(
            header=Header(
                frame_id=cmd.header.frame_id,
                stamp=cmd.header.stamp,
            ),
            child_frame_id=cmd.child_frame_id,
            transform=Transform(
                translation=cmd.pose.pose.position,
                rotation=cmd.pose.pose.orientation,
            ),
        )
        self.tf_pub.sendTransform(tf)


if __name__ == '__main__':
    rospy.init_node("gazebo_odometry_node")
    node = OdometryNode()
    rospy.spin()
