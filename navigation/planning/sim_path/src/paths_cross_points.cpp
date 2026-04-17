/**
 * @file paths_cross_points.cpp
 * @author Gavin Gao (cggos@outlook.com)
 * @brief
 * @version 0.1
 * @date 2025-08-27
 *
 * @copyright Copyright (c) 2025
 *
 */

#include "sim_path/paths_cross_points.h"

#include <limits>

namespace mapping {

bool PathsCrossPoints::isPointOnSegment(const Point& a, const Point& b, const Point& p, double epsilon) {
  // 检查三点是否共线
  double cross_product = (p.y - a.y) * (b.x - a.x) - (p.x - a.x) * (b.y - a.y);
  if (std::abs(cross_product) > epsilon) {
    return false;
  }

  // 检查点是否在线段范围内
  return distance(a, p) + distance(p, b) <= distance(a, b) + epsilon;
}

bool PathsCrossPoints::segmentsIntersect(const Point& p1, const Point& q1, const Point& p2, const Point& q2) {
  // 计算向量叉积
  auto cross = [](const Point& O, const Point& A, const Point& B) {
    return (A.x - O.x) * (B.y - O.y) - (A.y - O.y) * (B.x - O.x);
  };

  double d1 = cross(p1, q1, p2);
  double d2 = cross(p1, q1, q2);
  double d3 = cross(p2, q2, p1);
  double d4 = cross(p2, q2, q1);

  if (((d1 > 0 && d2 < 0) || (d1 < 0 && d2 > 0)) && ((d3 > 0 && d4 < 0) || (d3 < 0 && d4 > 0))) {
    return true;
  }

  // 检查端点是否在另一条线段上
  if (std::abs(d1) < 1e-9 && isPointOnSegment(p1, q1, p2)) return true;
  if (std::abs(d2) < 1e-9 && isPointOnSegment(p1, q1, q2)) return true;
  if (std::abs(d3) < 1e-9 && isPointOnSegment(p2, q2, p1)) return true;
  if (std::abs(d4) < 1e-9 && isPointOnSegment(p2, q2, q1)) return true;

  return false;
}

bool PathsCrossPoints::getSegmentIntersection(const Point& p1, const Point& p2, const Point& p3, const Point& p4,
                                              Point& intersection, float epsilon) {
  double x1 = p1.x, y1 = p1.y;
  double x2 = p2.x, y2 = p2.y;
  double x3 = p3.x, y3 = p3.y;
  double x4 = p4.x, y4 = p4.y;

  double denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4);

  if (std::abs(denom) < epsilon) {
    return false;  // 线段平行
  }

  double t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom;
  double u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom;

  // 检查交点是否在线段上
  if (t >= 0 && t <= 1 && u >= 0 && u <= 1) {
    intersection.x = x1 + t * (x2 - x1);
    intersection.y = y1 + t * (y2 - y1);
    return true;
  }

  return false;
}

std::vector<Point> PathsCrossPoints::findSegmentPathIntersections(const Point& segStart, const Point& segEnd,
                                                                  const std::vector<Point>& path) {
  std::vector<Point> intersections;

  for (size_t i = 0; i < path.size() - 1; ++i) {
    if (segmentsIntersect(segStart, segEnd, path[i], path[i + 1])) {
      // 计算两条线段的交点
      Point intersection;
      if (getSegmentIntersection(segStart, segEnd, path[i], path[i + 1], intersection)) {
        intersections.push_back(intersection);
      } else {
        // 如果无法计算精确交点，使用线段中点作为近似
        Point midpoint((segStart.x + segEnd.x) / 2, (segStart.y + segEnd.y) / 2);
        intersections.push_back(midpoint);
      }
    }
  }

  return intersections;
}

Point PathsCrossPoints::findClosestPointOnPath(const Point& point, const std::vector<Point>& path) {
  Point closestPoint;
  double minDistance = std::numeric_limits<double>::max();

  if (path.size() < 2) {
    return closestPoint;
  }

  for (size_t i = 0; i < path.size() - 1; ++i) {
    const Point& a = path[i];
    const Point& b = path[i + 1];

    // 计算点到线段的最近点
    double dx = b.x - a.x;
    double dy = b.y - a.y;
    double length = std::sqrt(dx * dx + dy * dy);

    if (length < 1e-9) {
      // 线段退化为点
      double dist = distance(point, a);
      if (dist < minDistance) {
        minDistance = dist;
        closestPoint = a;
      }
    } else {
      // 投影到线段上
      double t = ((point.x - a.x) * dx + (point.y - a.y) * dy) / (length * length);
      t = std::max(0.0, std::min(1.0, t));

      Point projection(a.x + t * dx, a.y + t * dy);
      double dist = distance(point, projection);

      if (dist < minDistance) {
        minDistance = dist;
        closestPoint = projection;
      }
    }
  }

  return closestPoint;
}

Point PathsCrossPoints::findLastCrossPoint(const std::vector<Point>& path_a, const std::vector<Point>& path_b,
                                           bool& found) {
  found = false;

  // 特殊情况1：path_b的起点到终点的轨迹长度在0.5米以内
  if (path_b.size() < 2) {
    return Point();  // 返回默认点，found仍为false
  }

  double totalLength = 0.0;
  for (size_t i = 0; i < path_b.size() - 1; ++i) {
    totalLength += distance(path_b[i], path_b[i + 1]);
  }

  if (totalLength <= 0.5) {
    return Point();  // 返回默认点，found仍为false
  }

  // 特殊情况2：距离path_b的终点的0.5米内没有找到path_a上的最近点
  Point endPoint = path_b.back();
  Point closestPoint = findClosestPointOnPath(endPoint, path_a);
  double endToClosestDistance = distance(endPoint, closestPoint);

  if (endToClosestDistance <= 0.5) {
    // 如果终点附近有path_a上的点，优先返回该点
    found = true;
    return closestPoint;
  }

  // 查找所有交叉点
  std::vector<std::pair<Point, int>> crossPoints;  // 交叉点和在path_b中的索引

  for (size_t i = 0; i < path_b.size() - 1; ++i) {
    std::vector<Point> intersections = findSegmentPathIntersections(path_b[i], path_b[i + 1], path_a);

    for (const auto& intersection : intersections) {
      crossPoints.push_back({intersection, static_cast<int>(i)});
    }
  }

  // 特殊情况3：path_b与path_a没有交叉点
  if (crossPoints.empty()) {
    return Point();  // 返回默认点，found仍为false
  }

  // 返回最后一个交叉点（按path_b上的顺序）
  found = true;
  return crossPoints.back().first;
}

}  // namespace map