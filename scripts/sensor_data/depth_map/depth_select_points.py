import cv2
import numpy as np


def select_show_depth_points(depth_path):

    depth_image = cv2.imread(depth_path, cv2.IMREAD_ANYDEPTH) / 1000.0

    display_image = cv2.normalize(depth_image, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
    display_image = cv2.cvtColor(display_image, cv2.COLOR_GRAY2BGR)

    used_positions = []

    def is_overlapping(x, y, text_size):
        for pos in used_positions:
            if abs(x - pos[0]) < text_size[0] and abs(y - pos[1]) < text_size[1]:
                return True
        return False

    # 回调函数，用于鼠标点击事件
    def click_event(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            depth_value = depth_image[y, x]
            text = f"{depth_value:.2f} ({x},{y})"

            text_size = cv2.getTextSize(text, font, 0.5, 1)[0]
            text_x = x + 15
            text_y = y - 15

            attempts = 0
            while is_overlapping(text_x, text_y, text_size) and attempts < 10:
                text_x = x + np.random.randint(-50, 50)
                text_y = y + np.random.randint(-50, 50)
                attempts += 1

            text_x = max(0, min(text_x, display_image.shape[1] - text_size[0]))
            text_y = max(0, min(text_y, display_image.shape[0] - text_size[1]))

            used_positions.append((text_x, text_y))

            cv2.circle(display_image, (x, y), 1, (0, 0, 255), -1)  # 红色圆点
            cv2.arrowedLine(
                display_image, (x, y), (text_x, text_y), (0, 255, 0), 1
            )  # 绿色箭头

            # 绘制文字
            cv2.putText(
                display_image,
                text,
                (text_x, text_y),
                font,
                0.5,
                (0, 0, 255),
                1,
                cv2.LINE_AA,
            )

            cv2.imshow("Depth Image", display_image)

    if depth_image is None:
        print("Error: Unable to read the depth image.")
    else:
        font = cv2.FONT_HERSHEY_SIMPLEX

        cv2.namedWindow("Depth Image")
        cv2.setMouseCallback("Depth Image", click_event)

        while True:
            cv2.imshow("Depth Image", display_image)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cv2.destroyAllWindows()


if __name__ == "__main__":
    select_show_depth_points(
        "7.voa动态测试20240826/7.static.1.9m/depth/depth_2109947.png"
    )
