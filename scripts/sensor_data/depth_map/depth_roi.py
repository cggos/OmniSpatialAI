import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
import re

num_select_points = 15

def read_u16_image(file_path):
    # Extract width and height from filename using regular expressions
    match = re.search(r'_(\d+)_(\d+)\.u16$', file_path)
    if not match:
        raise ValueError("Filename format incorrect. Unable to extract dimensions.")
    
    width = int(match.group(1))
    height = int(match.group(2))

    # Read the .u16 file as a 1D array of 16-bit unsigned integers
    image_data = np.fromfile(file_path, dtype=np.uint16)

    # Reshape the data into a 2D array (height, width)
    image = image_data.reshape((height, width))

    # Optional: Normalize for viewing
    # image_normalized = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    
    return image

# 获取文件夹中所有图像文件的路径
def get_image_paths(folder):
    image_paths = [os.path.join(folder, f) for f in sorted(os.listdir(folder)) if f.endswith(('.png', '.tiff', '.bmp','.u16'))]
    return image_paths

# 鼠标点击事件，用于选择点
def select_points(event, x, y, flags, param):
    global points, img_copy
    if event == cv2.EVENT_LBUTTONDOWN:
        points.append((x, y))
        cv2.circle(img_copy, (x, y), 5, (0, 255, 0), -1)
        cv2.imshow("Select Points", img_copy)
        if len(points) >= num_select_points:
            print(f"Selected points: {points}")

# 鼠标框选事件，用于选择ROI区域
def select_roi(event, x, y, flags, param):
    global roi_start, roi_end, selecting_roi, img_copy
    if event == cv2.EVENT_LBUTTONDOWN:
        roi_start = (x, y)
        selecting_roi = True
    elif event == cv2.EVENT_MOUSEMOVE and selecting_roi:
        img_copy = img_original.copy()
        roi_end = (x, y)
        cv2.rectangle(img_copy, roi_start, roi_end, (0, 255, 0), 2)
        cv2.imshow("Select ROI", img_copy)
    elif event == cv2.EVENT_LBUTTONUP:
        roi_end = (x, y)
        selecting_roi = False
        cv2.rectangle(img_copy, roi_start, roi_end, (0, 255, 0), 2)
        cv2.imshow("Select ROI", img_copy)
        print(f"Selected ROI: {roi_start} to {roi_end}")

# 读取文件夹中的所有深度图像
folder_path = '/home/user/proj_camera_sensor_test/imgs_1029/90_shadow'  # 替换为实际的文件夹路径
image_paths = get_image_paths(folder_path)
# depth_images = [cv2.imread(p, cv2.IMREAD_UNCHANGED) / 1000. for p in image_paths]
depth_images = [read_u16_image(p) / 1000. for p in image_paths]

# 选择中间的图像进行点选操作
middle_index = len(depth_images) // 2
img_original = depth_images[middle_index].copy()
img_copy = img_original.copy()

# 选择点
points = []
# cv2.namedWindow("Select Points")
cv2.imshow("Select Points", img_copy)
cv2.setMouseCallback("Select Points", select_points)
cv2.waitKey(0)  # 等待用户选择点

# 确保选择了正确数量的点
if len(points) != num_select_points:
    print(f"Error: You must select exactly {num_select_points} points.")
    exit()

# 选择ROI区域
roi_start, roi_end = None, None
selecting_roi = False
cv2.namedWindow("Select ROI")
cv2.imshow("Select ROI", img_copy)
cv2.setMouseCallback("Select ROI", select_roi)
cv2.waitKey(0)  # 等待用户选择ROI

if roi_start is None or roi_end is None:
    print("Error: You must select an ROI.")
    exit()

# 统计每个点在所有图像中的深度值变化
depth_values = np.zeros((num_select_points, len(depth_images)), dtype=np.float32)
for i, (x, y) in enumerate(points):
    for j, img in enumerate(depth_images):
        depth_values[i, j] = img[y, x]

# 统计ROI区域内的平均深度变化
roi_depth_values = []
for img in depth_images:
    roi = img[roi_start[1]:roi_end[1], roi_start[0]:roi_end[0]]
    roi_depth = np.mean(roi[roi > 0])  # 只考虑有效深度值
    roi_depth_values.append(roi_depth)

# 绘制每个点的深度值变化曲线
plt.figure(figsize=(15, 10))
for i in range(num_select_points):
    plt.plot(depth_values[i], label=f"Point {i+1} ({points[i][0]}, {points[i][1]})")

plt.title("Depth Values for Selected Points Across All Images")
plt.xlabel("Image Index")
plt.ylabel("Depth Value")
plt.legend()
plt.grid(True)
plt.show()

# 绘制ROI区域的平均深度变化曲线
plt.figure(figsize=(15, 10))
plt.plot(roi_depth_values, label="ROI Average Depth")
plt.title("Average Depth in ROI Across All Images")
plt.xlabel("Image Index")
plt.ylabel("Average Depth Value")
plt.legend()
plt.grid(True)
plt.show()

# 输出各点的深度平均值
average_depths = np.mean(depth_values, axis=1)
print("Average Depth Values for Each Point:")
for i, avg_depth in enumerate(average_depths):
    print(f"Point {i+1} ({points[i][0]}, {points[i][1]}): {avg_depth:.3f} meters")