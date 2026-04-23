# https://gist.github.com/pryre/8d6f44e18d52efb616f64403de0838ef

import sys
import cv2
import rospy
from cv_bridge import CvBridge
from sensor_msgs.msg import Image
from datetime import datetime
import os
import time


class ROSImage2Video:
    def __init__(self, time_name=None) -> None:
        video_dir = sys.argv[1]
        video_name = sys.argv[2]
        os.makedirs(video_dir, exist_ok=True)
        self.video_path = "{}/{}_{}.avi".format(video_dir, video_name, time_name)
        print("The video save path is: ", self.video_path)

        print("**********************************************")

        self.img_sub = rospy.Subscriber(
            "/camera/metoak/color1/image_raw", Image, self.callback
        )

        self.is_inited = False
        self.flag = False

        self.vw = None
        self.count = 0

        self.previous_image = None

    def callback(self, data):
        br = CvBridge()

        frame = br.imgmsg_to_cv2(data, "bgr8")

        print(frame.shape)

        if not self.is_inited:
            fps = 20
            height, width, _ = frame.shape
            # fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            fourcc = cv2.VideoWriter_fourcc(*"FFV1")
            if self.vw is None:
                self.vw = cv2.VideoWriter(self.video_path, fourcc, fps, (width, height))
            self.is_inited = True
            print("inited!")
        else:
            if False:
                # cv2.imshow("camera", frame)
                # k = cv2.waitKey(5)
                if self.flag:
                    self.vw.write(frame)
                    print("recording frame count {}", format(self.count))
                    self.count += 1
                if k == ord("s"):
                    self.flag = True
                    print("start recording video {}".format(self.video_path))
                elif k & 0xFF == ord("q") or k == 27:
                    print("done")
                    self.shutdown()
            else:
                if not self.is_same_image(frame):
                    self.vw.write(frame)
                    print("recording frame count {}", format(self.count))
                    self.count += 1
                    self.previous_image = frame
                    # time.sleep(0.015)

    def shutdown(self):
        if self.img_sub is not None:
            self.img_sub.unregister()
        self.vw.release()
        cv2.destroyAllWindows()

    def is_same_image(self, new_image):
        if self.previous_image is not None:
            return (new_image == self.previous_image).all()
        else:
            return False


if __name__ == "__main__":
    rospy.init_node("video_sub_py", anonymous=True)

    now = datetime.now()
    time_name = (
        str(now.year)
        + str(now.month).zfill(2)
        + str(now.day).zfill(2)
        + str(now.hour).zfill(2)
        + str(now.minute).zfill(2)
    )

    iv = ROSImage2Video(time_name=time_name)
    rospy.on_shutdown(iv.shutdown)

    rospy.spin()
