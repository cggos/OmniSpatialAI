#!/usr/bin/env python3
"""
3D点云数据可视化工具
读取每行代表一个3D点（3个点逗号隔开）的文件，使用Open3D显示并保存为PLY文件
"""

import numpy as np
import open3d as o3d
import argparse
import os


def read_point_cloud_file(file_path):
    """
    读取3D点云数据文件
    每行格式: x,y,z (逗号分隔)
    
    Args:
        file_path (str): 点云文件路径
        
    Returns:
        np.ndarray: 点云数据数组，形状为(N, 3)
    """
    points = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith('#'):  # 跳过空行和注释行
                    continue

                try:
                    # 分割并转换为浮点数
                    coords = line.split(';')
                    if len(coords) != 3:
                        print(f"警告: 第{line_num}行数据格式错误，应为3个数值，实际为{len(coords)}个")
                        continue

                    x, y, z = map(float, coords)
                    points.append([x, y, z])

                except ValueError as e:
                    print(f"警告: 第{line_num}行数据转换错误: {e}")
                    continue

    except FileNotFoundError:
        print(f"错误: 文件 '{file_path}' 不存在")
        return None
    except Exception as e:
        print(f"错误: 读取文件时发生异常: {e}")
        return None

    if not points:
        print("错误: 没有读取到有效的点云数据")
        return None

    return np.array(points, dtype=np.float64)


def create_point_cloud(points):
    """
    创建Open3D点云对象并过滤Z坐标小于0.05m的点
    
    Args:
        points (np.ndarray): 点云数据数组
        
    Returns:
        tuple: (o3d.geometry.PointCloud, int) - Open3D点云对象和过滤掉的点数量
    """
    # 统计Z坐标小于0.05m的点
    z_threshold = 0.01
    mask = points[:, 2] >= z_threshold
    filtered_points = points[mask]
    filtered_count = len(points) - len(filtered_points)
    
    if filtered_count > 0:
        print(f"过滤掉 {filtered_count} 个Z坐标小于{z_threshold}m的点")
    
    point_cloud = o3d.geometry.PointCloud()
    point_cloud.points = o3d.utility.Vector3dVector(filtered_points)
    return point_cloud, filtered_count


def visualize_point_cloud(point_cloud, window_name="3D点云可视化"):
    """
    可视化点云
    
    Args:
        point_cloud (o3d.geometry.PointCloud): Open3D点云对象
        window_name (str): 窗口名称
    """
    # 设置点云颜色（基于坐标的渐变色）
    points = np.asarray(point_cloud.points)
    # if len(points) > 0:
    #     # 基于Z坐标计算颜色
    #     z_coords = points[:, 2]
    #     z_normalized = (z_coords - z_coords.min()) / (z_coords.max() - z_coords.min())
    #     colors = np.zeros((len(points), 3))
    #     colors[:, 0] = z_normalized  # R通道
    #     colors[:, 1] = 1 - z_normalized  # G通道
    #     colors[:, 2] = 0.5  # B通道
    #     point_cloud.colors = o3d.utility.Vector3dVector(colors)

    # 添加坐标轴
    coordinate_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=1.0)

    # 可视化
    # 设置相机从Z轴俯视
    points_center = points.mean(axis=0)
    lookat = points_center
    up = np.array([0, -1, 0])  # Y轴向下
    front = np.array([0, 0, -1])  # 向Z轴负方向看
    zoom = 0.2

    o3d.visualization.draw_geometries(
        [point_cloud, coordinate_frame],
        window_name=window_name,
        width=800,
        height=600,
        left=50,
        top=50,
        point_show_normal=False,
        lookat=lookat,
        up=up,
        front=front,
        zoom=zoom
    )


def save_point_cloud_ply(point_cloud, output_path):
    """
    保存点云为PLY文件
    
    Args:
        point_cloud (o3d.geometry.PointCloud): Open3D点云对象
        output_path (str): 输出PLY文件路径
    """
    try:
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # 保存为PLY文件
        o3d.io.write_point_cloud(output_path, point_cloud)
        print(f"点云已保存到: {output_path}")

    except Exception as e:
        print(f"错误: 保存PLY文件时发生异常: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="3D点云数据可视化工具")
    parser.add_argument("input_file", help="输入点云文件路径")
    parser.add_argument("-o", "--output", help="输出PLY文件路径", default=None)
    parser.add_argument("--no-visualize", action="store_true", help="跳过可视化显示")
    parser.add_argument("--window-name", default="3D点云可视化", help="可视化窗口名称")

    args = parser.parse_args()

    # 如果未指定输出路径，则保存在输入文件同级目录
    if args.output is None:
        input_dir = os.path.dirname(args.input_file)
        input_name = os.path.splitext(os.path.basename(args.input_file))[0]
        args.output = os.path.join(input_dir, f"{input_name}.ply")

    # 读取点云数据
    print(f"正在读取点云文件: {args.input_file}")
    points = read_point_cloud_file(args.input_file)

    if points is None:
        return

    print(f"成功读取 {len(points)} 个点")
    print(f"点云范围: X[{points[:, 0].min():.3f}, {points[:, 0].max():.3f}], "
          f"Y[{points[:, 1].min():.3f}, {points[:, 1].max():.3f}], "
          f"Z[{points[:, 2].min():.3f}, {points[:, 2].max():.3f}]")

    # 创建Open3D点云对象
    point_cloud, filtered_count = create_point_cloud(points)

    # 可视化
    if not args.no_visualize:
        print("正在显示点云...")
        visualize_point_cloud(point_cloud, args.window_name)

    # 保存为PLY文件
    print(f"正在保存为PLY文件: {args.output}")
    save_point_cloud_ply(point_cloud, args.output)

    print("处理完成!")


if __name__ == "__main__":
    main()
