/**
 * @file paths_cross_points.h
 * @author Gavin Gao (cggos@outlook.com)
 * @brief
 * @version 0.1
 * @date 2025-08-27
 *
 * @copyright Copyright (c) 2025
 *
 */

#pragma once

#include <cmath>
#include <memory>
#include <vector>

namespace mapping {

struct Point {
  double x, y;
  Point() : x(0), y(0) {}
  Point(double x_, double y_) : x(x_), y(y_) {}
};

class PathsCrossPoints {
 public:
  PathsCrossPoints() = default;

  /**
   * @brief 查找path_b与path_a的最后一个交叉点
   *
   * @details 输入两条二维轨迹点PathA和PathB，PathB从起点到终点可能会与PathA有交叉，
   *          找出PathB从起点到终点与PathA上的最后一个交叉点，并返回该交叉点；
   *          如果path_b的终点与patha上的最近点距离0.5米内，则优先返回该点；
   *
   *          如果有以下几种情况，返回False：
   *          1）如果PathB的起点到终点的轨迹长度在0.5米以内
   *          2）距离PathB的终点的0.5米内没有找到PathA上的最近点
   *          3）PathB与PathA没有交叉点
   *
   * @param path_a
   * @param path_b
   * @param found
   * @return Point
   */
  Point findLastCrossPoint(const std::vector<Point>& path_a, const std::vector<Point>& path_b, bool& found);

  using Ptr = std::shared_ptr<PathsCrossPoints>;

 private:
  // 计算两点间距离
  double distance(const Point& a, const Point& b) {
    return std::sqrt((a.x - b.x) * (a.x - b.x) + (a.y - b.y) * (a.y - b.y));
  }

  bool isPointOnSegment(const Point& a, const Point& b, const Point& p, double epsilon = kEpsilon);

  // 计算点到路径的最近点
  Point findClosestPointOnPath(const Point& point, const std::vector<Point>& path);

  // 检查两条线段是否相交
  bool segmentsIntersect(const Point& p1, const Point& q1, const Point& p2, const Point& q2);

  // 计算两条线段的交点
  bool getSegmentIntersection(const Point& p1, const Point& p2, const Point& p3, const Point& p4, Point& intersection,
                              float epsilon = kEpsilon);

  // 查找线段与路径的交点
  std::vector<Point> findSegmentPathIntersections(const Point& segStart, const Point& segEnd,
                                                  const std::vector<Point>& path);

 private:
  static constexpr float kEpsilon = 0.01;
};

}  // namespace map