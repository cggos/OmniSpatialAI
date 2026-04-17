/**
 * @file test_cross_points.cpp
 * @author Gavin Gao (cggos@outlook.com)
 * @brief
 * @version 0.1
 * @date 2025-08-27
 *
 * @copyright Copyright (c) 2025
 *
 */

#include <iostream>

#include "sim_path/paths_cross_points.h"

using namespace mapping;

int main() {
  PathsCrossPoints::Ptr paths_cross_points_ptr_ = std::make_shared<PathsCrossPoints>();

  std::vector<Point> path_a = {
      Point(0, 0), Point(2, 0), Point(2, 2), Point(0, 2), Point(0, 0)  // 闭合正方形
  };

  std::vector<Point> path_b = {
      Point(-1, 1), Point(3, 1)  // 横穿正方形的线段
  };

  bool found;
  Point result = paths_cross_points_ptr_->findLastCrossPoint(path_a, path_b, found);

  if (found) {
    std::cout << "找到交叉点: (" << result.x << ", " << result.y << ")" << std::endl;
  } else {
    std::cout << "未找到交叉点或不满足条件" << std::endl;
  }

  return 0;
}