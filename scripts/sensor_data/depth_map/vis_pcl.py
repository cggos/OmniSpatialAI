import os
import re
import numpy as np
import cv2
import open3d as o3d
import matplotlib.pyplot as plt

# conda activate torch
import math
import pcl

# 相机内参
fx = 377.657135
fy = 377.618896
cx = 322.281921
cy = 188.960953

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

def depth_to_point_cloud(depth_image, fx, fy, cx, cy):
    height, width = depth_image.shape
    i, j = np.indices((height, width))
    z = depth_image.astype(float) / 1000.0  # 假设深度图的单位是毫米，将其转换为米

    x = (j - cx) * z / fx
    y = (i - cy) * z / fy
    points = np.stack((x, y, z), axis=-1).reshape(-1, 3)

    points = points[(z.flatten() > 0) & (z.flatten() < 2.0)]

    return points


def display_point_cloud(points):
    point_cloud = o3d.geometry.PointCloud()
    point_cloud.points = o3d.utility.Vector3dVector(points)

    coordinate_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(
        size=0.1, origin=[0, 0, 0]
    )

    o3d.visualization.draw_geometries([point_cloud, coordinate_frame])
    # o3d.visualization.draw_geometries([point_cloud])


def display_point_cloud_with_height_coloring(points):
    # 创建点云对象
    point_cloud = o3d.geometry.PointCloud()
    point_cloud.points = o3d.utility.Vector3dVector(points)

    z_values = np.asarray(point_cloud.points)[:, 1]
    z_min = z_values.min()
    z_max = z_values.max()
    z_normalized = (z_values - z_min) / (z_max - z_min)

    colors = plt.get_cmap("viridis")(z_normalized)[:, :3]
    point_cloud.colors = o3d.utility.Vector3dVector(colors)

    coordinate_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(
        size=0.1, origin=[0, 0, 0]
    )

    vis = o3d.visualization.VisualizerWithEditing()
    vis.create_window()
    vis.add_geometry(point_cloud)
    vis.add_geometry(coordinate_frame)
    vis.run()
    vis.destroy_window()

    picked_points_indices = vis.get_picked_points()

    if picked_points_indices:
        print("Picked points:")
        for idx in picked_points_indices:
            point = point_cloud.points[idx]
            print(f"Index: {idx}, Coordinates: {point}")
    else:
        print("No points were selected.")


def main():

    filename = "/home/user/proj_camera_sensor_test/imgs_1029/90_shadow/depth_402637068_5975_640_480.u16"
    print(filename)

    # depth_image = cv2.imread(filename, cv2.IMREAD_UNCHANGED)
    depth_image = read_u16_image(filename)

    if depth_image is not None:
        points = depth_to_point_cloud(depth_image, fx, fy, cx, cy)
        if points.size != 0:
            display_point_cloud_with_height_coloring(points)


if __name__ == "__main__":
    main()
