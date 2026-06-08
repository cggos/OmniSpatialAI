#!/usr/bin/env python3
"""
Relay laser_scan_matcher's /odom topic as odom→base_link TF at 100 Hz.

laser_scan_matcher publishes TF only at the laser scan rate (10 Hz).
Each new scan then tries to look up TF at the scan's timestamp, which is
always ahead of the last published TF → continuous "extrapolation" warnings.

By publishing TF continuously at 100 Hz from the accumulated /odom pose,
the TF buffer stays dense and laser_scan_matcher's internal TF lookups
always find a valid entry.  Set publish_tf: false in laser_scan_matcher.
"""
import rospy
import tf2_ros
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped

_pose = None

def _odom_cb(msg):
    global _pose
    _pose = msg.pose.pose


def main():
    rospy.init_node('laser_odom_tf_relay')
    rospy.Subscriber('/odom', Odometry, _odom_cb)

    br = tf2_ros.TransformBroadcaster()
    rate = rospy.Rate(100)

    t = TransformStamped()
    t.header.frame_id = 'odom'
    t.child_frame_id = 'base_link'
    t.transform.rotation.w = 1.0  # identity until first /odom arrives

    while not rospy.is_shutdown():
        t.header.stamp = rospy.Time.now()
        if _pose is not None:
            t.transform.translation.x = _pose.position.x
            t.transform.translation.y = _pose.position.y
            t.transform.translation.z = _pose.position.z
            t.transform.rotation = _pose.orientation
        br.sendTransform(t)
        rate.sleep()


if __name__ == '__main__':
    main()
