import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
import re


folder_path = "/home/user/proj_camera_sensor_test/imgs_1029/90_shadow"
num_select_points = 15
num_rois = 7
rois = []

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

def get_image_paths(folder):
    image_paths = [
        os.path.join(folder, f)
        for f in sorted(os.listdir(folder))
        if (f.endswith((".png")) or f.endswith((".u16")))
    ]
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


def select_roi(event, x, y, flags, param):
    global roi_start, roi_end, selecting_roi, img_copy, rois
    if event == cv2.EVENT_LBUTTONDOWN:
        if len(rois) < num_rois:
            roi_start = (x, y)
            selecting_roi = True
    elif event == cv2.EVENT_MOUSEMOVE and selecting_roi:
        img_copy = img_copy.copy()
        roi_end = (x, y)
        cv2.rectangle(img_copy, roi_start, roi_end, (0, 255, 0), 2)
        cv2.imshow("Select ROI", img_copy)
    elif event == cv2.EVENT_LBUTTONUP:
        roi_end = (x, y)
        selecting_roi = False
        cv2.rectangle(img_copy, roi_start, roi_end, (0, 255, 0), 2)
        rois.append((roi_start, roi_end))
        cv2.imshow("Select ROI", img_copy)
        print(f"Selected ROI: {roi_start} to {roi_end}")


image_paths = get_image_paths(folder_path)
# depth_images = [cv2.imread(p, cv2.IMREAD_UNCHANGED) / 1000.0 for p in image_paths]
depth_images = [read_u16_image(p) / 1000.0 for p in image_paths]



middle_index = len(depth_images) // 2
img_original = depth_images[middle_index].copy()


depth_map_normalized = cv2.normalize(img_original, None, 0, 255, cv2.NORM_MINMAX)
depth_map_8bit = np.uint8(depth_map_normalized)


depth_map_color = cv2.applyColorMap(depth_map_8bit, cv2.COLORMAP_JET)


cv2.imshow("Colored Depth Map", depth_map_color)
cv2.waitKey(0)
img_copy = depth_map_color.copy()

points = []
cv2.namedWindow("Select Points")
cv2.imshow("Select Points", img_copy)
cv2.setMouseCallback("Select Points", select_points)
cv2.waitKey(0)

if len(points) != num_select_points:
    print(f"Error: You must select exactly {num_select_points} points.")
    exit()

depth_values = np.zeros((num_select_points, len(depth_images)), dtype=np.float32)
for i, (x, y) in enumerate(points):
    for j, img in enumerate(depth_images):
        depth_values[i, j] = img[y, x]

plt.figure(figsize=(15, 10))
for i in range(num_select_points):
    plt.plot(depth_values[i], label=f"Point {i+1} ({points[i][0]}, {points[i][1]})")

plt.title("Depth Values for Selected Points Across All Images")
plt.xlabel("Image Index")
plt.ylabel("Depth Value")
plt.legend()
plt.grid(True)
# plt.show()
plt.savefig("depth_point.png")

roi_start, roi_end = None, None
selecting_roi = False
cv2.namedWindow("Select ROI")
# cv2.imshow("Select ROI", img_copy)
cv2.setMouseCallback("Select ROI", select_roi)

while len(rois) < num_rois:
    cv2.waitKey(0)

for i, (start, end) in enumerate(rois):
    print(f"ROI {i+1}: {start} to {end}")

roi_depth_values = {i: [] for i in range(len(rois))}

for img in depth_images:
    for i, (start, end) in enumerate(rois):
        roi = img[start[1] : end[1], start[0] : end[0]]
        roi_depth = np.mean(roi[roi > 0])
        roi_depth_values[i].append(roi_depth)

plt.figure(figsize=(15, 10))
for i, depths in roi_depth_values.items():
    plt.plot(depths, label=f"ROI {i+1} Average Depth")

plt.title("Average Depth in ROIs Across All Images")
plt.xlabel("Image Index")
plt.ylabel("Average Depth Value")
plt.legend()
plt.grid(True)
# plt.show()

average_depths = np.mean(depth_values, axis=1)
print("Average Depth Values for Each Point:")
for i, avg_depth in enumerate(average_depths):
    print(f"Point {i+1} ({points[i][0]}, {points[i][1]}): {avg_depth:.3f} meters")
