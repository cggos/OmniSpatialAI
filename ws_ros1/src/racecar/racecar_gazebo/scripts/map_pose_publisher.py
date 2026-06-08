#!/usr/bin/env python3
"""
Publish robot pose in the map frame as nav_msgs/Odometry on /pf/pose/odom.

path_pursuit.py compares robot position from /pf/pose/odom against the
global plan (map frame) using raw coordinate arithmetic, so both must be in
the same frame.

With gazebo_odometry_odom.py the Gazebo world coordinates happen to equal
map coordinates, but laser_scan_matcher starts at (0,0) in the odom frame
which mismatches map-frame path points.  This node reads map→base_link from
TF (computed by AMCL: map→odom + odom→base_link) and republishes at 20 Hz.
"""
import rospy
import tf2_ros
from nav_msgs.msg import Odometry


def main():
    rospy.init_node('map_pose_publisher')
    tf_buffer = tf2_ros.Buffer()
    tf2_ros.TransformListener(tf_buffer)
    pub = rospy.Publisher('/odom_fusion', Odometry, queue_size=1)
    rate = rospy.Rate(20)

    msg = Odometry()
    msg.header.frame_id = 'map'
    msg.child_frame_id = 'base_link'

    while not rospy.is_shutdown():
        try:
            t = tf_buffer.lookup_transform('map', 'base_link', rospy.Time(0))
            msg.header.stamp = t.header.stamp
            msg.pose.pose.position.x = t.transform.translation.x
            msg.pose.pose.position.y = t.transform.translation.y
            msg.pose.pose.position.z = t.transform.translation.z
            msg.pose.pose.orientation = t.transform.rotation
            pub.publish(msg)
        except Exception:
            pass
        rate.sleep()


if __name__ == '__main__':
    main()
