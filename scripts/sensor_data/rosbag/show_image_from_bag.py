import rospy
import rosbag
from sensor_msgs.msg import Image
import cv2
from cv_bridge import CvBridge
import matplotlib.pyplot as plt
import numpy as np

rospy.init_node("extract_depth_image_from_rosbag")


bag = rosbag.Bag(
    "Gongzhuang_Metoak_Nanjing99_Lcation2_202404071409_2024-03-26-06-55-58.bag"
)


bridge = CvBridge()

depth_image = None
rgb_image = None


for topic, msg, t in bag.read_messages():
    if topic == "/camera/metoak/depth/image_rect_raw":  # rostopic
        # ROS -> OpenCV
        cv_image = bridge.imgmsg_to_cv2(msg, desired_encoding="passthrough")
        cv_image = (cv_image / cv_image.max() * 255).astype(np.uint8)
        cv_image = cv2.applyColorMap(cv_image, cv2.COLORMAP_JET)  # vis

    if topic == "/camera/metoak/color1/image_raw":  # rostopic
        rgb_image = bridge.imgmsg_to_cv2(msg, desired_encoding="passthrough")
        # rgb_image = cv2.cvtColor(rgb_image, cv2.COLOR_BGR2RGB)

    if cv_image is not None and rgb_image is not None:
        # plt.subplot(1,2,1)
        # plt.imshow(rgb_image)
        # plt.subplot(1,2,2)
        # plt.imshow(cv_image)
        # plt.show()
        cv2.imshow("depth", cv_image)
        cv2.imshow("rgb_image", rgb_image)
        cv2.waitKey(0)


# 关闭ROS bag文件
bag.close()
