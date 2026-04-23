import os
import re
import numpy as np
import cv2
import open3d as o3d
import matplotlib.pyplot as plt

# conda activate torch
import math
import pcl

# Camera intrinsic parameters
# metoak
# fx = 377.657135
# fy = 377.618896
# cx = 322.281921
# cy = 188.960953

# orbbec
fx = 294.827
fy = 294.827
cx = 318.800
cy = 237.49

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

    return image

def depth_to_point_cloud(depth_image, fx, fy, cx, cy):
    height, width = depth_image.shape
    i, j = np.indices((height, width))
    z = depth_image.astype(float) / 1000.0  # Assume depth image in millimeters; convert to meters

    x = (j - cx) * z / fx
    y = (i - cy) * z / fy
    points = np.stack((x, y, z), axis=-1).reshape(-1, 3)

    # Remove points with zero or excessive depth
    points = points[(z.flatten() > 0) & (z.flatten() < 2.0)]

    return points


def display_point_cloud_with_height_coloring(vis, point_cloud):
    vis.clear_geometries()
    vis.add_geometry(point_cloud)
    vis.update_renderer()
    
def create_point_cloud(points):
    # Create the point cloud with height-based coloring
    point_cloud = o3d.geometry.PointCloud()
    point_cloud.points = o3d.utility.Vector3dVector(points)

    # Add color based on height (y-axis)
    z_values = np.asarray(point_cloud.points)[:, 1]
    z_min, z_max = z_values.min(), z_values.max()
    z_normalized = (z_values - z_min) / (z_max - z_min)
    colors = plt.get_cmap("viridis")(z_normalized)[:, :3]
    point_cloud.colors = o3d.utility.Vector3dVector(colors)
    
    return point_cloud
    
class DepthImageVisualizer:
    def __init__(self, directory):
        self.directory = directory
        self.depth_images = sorted(
            [os.path.join(directory, f) for f in os.listdir(directory) if "_depth_" in f and f.endswith(".png")]
        )
        self.index = 0
        self.vis = o3d.visualization.VisualizerWithKeyCallback()
        self.vis.create_window()
        
        # Set up key callbacks
        self.vis.register_key_callback(ord("D"), self.next_image)
        self.vis.register_key_callback(ord("A"), self.previous_image)

        # Display the first image's point cloud
        self.update_point_cloud()

    def next_image(self, vis):
        if self.index < len(self.depth_images) - 1:
            self.index += 1
            self.update_point_cloud()

    def previous_image(self, vis):
        if self.index > 0:
            self.index -= 1
            self.update_point_cloud()

    def update_point_cloud(self):
        current_image_path = self.depth_images[self.index]
        print(f"Displaying {current_image_path}")
        
        depth_image = cv2.imread(current_image_path, cv2.IMREAD_UNCHANGED)
        points = depth_to_point_cloud(depth_image, fx, fy, cx, cy)
        point_cloud = create_point_cloud(points)
        display_point_cloud_with_height_coloring(self.vis, point_cloud)
        
        # Customize the initial view direction
        view_control = self.vis.get_view_control()
        # view_control.set_lookat([0, 0, 0])  # Look-at point (center of point cloud)
        view_control.set_front([1.0, -1.0, -0.5])  # Flip the direction of the view
        view_control.set_up([0, -1, 0])  # Adjust up vector (may not need to change)
        view_control.set_zoom(0.5)  # Zoom level

    def run(self):
        self.vis.run()
        self.vis.destroy_window()

def main():
    # Directory containing depth images
    directory = "/media/user/My Passport/ORBBEC_DATA/1115_1020/video"
    visualizer = DepthImageVisualizer(directory)
    visualizer.run()

if __name__ == "__main__":
    main()
