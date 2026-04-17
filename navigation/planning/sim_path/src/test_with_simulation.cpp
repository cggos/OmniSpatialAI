/**
 * @file test_with_simulation.cpp
 * @author Gavin Gao (cggos@outlook.com)
 * @brief
 * @version 0.1
 * @date 2025-08-27
 *
 * @copyright Copyright (c) 2025
 *
 */

#include <iostream>
#include <memory>
#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <random>
#include <vector>

#include "sim_path/paths_cross_points.h"

namespace mapping {

class PathSimulation {
 public:
  PathSimulation()
      : scale_factor_(100.0),  // 1米 = 100像素
        is_path_b_ready_(false),
        is_calculated_(false) {
    srand(time(0));

    cv::namedWindow(window_name_.c_str(), cv::WINDOW_AUTOSIZE);
    cv::setMouseCallback(window_name_.c_str(), onMouse, this);

    canvas_ = cv::Mat(800, 1200, CV_8UC3, cv::Scalar(255, 255, 255));
    draw_mode_ = ModeDrawPathA;
    selection_mode_ = SelectStart;

    updateDisplay();
  }

  ~PathSimulation() { cv::destroyAllWindows(); }

  void run() {
    std::cout << "操作说明：" << std::endl;
    std::cout << "1. 模式1：绘制PathA（闭合轨迹） - 左键点击绘制点，中键点击完成闭合" << std::endl;
    std::cout << "2. 模式2：选择PathB起点和终点 - 左键点击选择两个点" << std::endl;
    std::cout << "3. 按Enter键计算交叉点" << std::endl;
    std::cout << "4. 按r键重置" << std::endl;
    std::cout << "5. 按q键退出" << std::endl;
    std::cout << "6. 当前使用的坐标比例：100像素 = 1米" << std::endl;

    while (true) {
      int key = cv::waitKey(30);

      if (key == 'q' || key == 'Q') {
        break;
      } else if (key == 'r' || key == 'R') {
        reset();
      } else if (key == 13) {  // Enter键
        calculate_cross_point();
      }
    }
  }

 private:
  enum DrawingMode { ModeDrawPathA, ModeSelectPoints };

  enum SelectMode { SelectStart, SelectEnd };

  struct PointPixel {
    int x, y;
    PointPixel() : x(0), y(0) {}
    PointPixel(int x_, int y_) : x(x_), y(y_) {}

    bool operator==(const PointPixel& other) const { return x == other.x && y == other.y; }
    bool operator!=(const PointPixel& other) const { return !((*this) == other); }
  };

  static void onMouse(int event, int x, int y, int flags, void* userdata) {
    PathSimulation* self = static_cast<PathSimulation*>(userdata);
    self->handleMouseEvent(event, x, y, flags);
  }

  void handleMouseEvent(int event, int x, int y, int flags) {
    if (event == cv::EVENT_LBUTTONDOWN) {
      if (draw_mode_ == ModeDrawPathA) {
        path_a_points_pixel_.emplace_back(x, y);
        updateDisplay();
      } else if (draw_mode_ == ModeSelectPoints) {
        if (selection_mode_ == SelectStart) {
          path_b_start_pixel_ = PointPixel(x, y);
          selection_mode_ = SelectEnd;
          updateDisplay();
        } else if (selection_mode_ == SelectEnd) {
          path_b_end_pixel_ = PointPixel(x, y);
          generate_random_path_b();
          is_path_b_ready_ = true;
          is_calculated_ = false;
          updateDisplay();
        }
      }
    } else if (event == cv::EVENT_MBUTTONDOWN && draw_mode_ == ModeDrawPathA && path_a_points_pixel_.size() > 2) {
      // 关闭路径
      draw_mode_ = ModeSelectPoints;
      selection_mode_ = SelectStart;
      updateDisplay();
    }
  }

  void generate_random_path_b() {
    if (path_b_start_pixel_ == path_b_end_pixel_) return;

    path_b_points_pixel_.clear();

    // 从起点开始
    path_b_points_pixel_.push_back(path_b_start_pixel_);

    int steps = 50;

    if (std::abs(path_b_end_pixel_.x - path_b_start_pixel_.x) < 50 &&
        std::abs(path_b_end_pixel_.y - path_b_start_pixel_.y) < 50) {
      // 简单线性插值
      for (int i = 1; i <= steps; ++i) {
        double t = (double)i / steps;
        int x = path_b_start_pixel_.x + t * (path_b_end_pixel_.x - path_b_start_pixel_.x);
        int y = path_b_start_pixel_.y + t * (path_b_end_pixel_.y - path_b_start_pixel_.y);
        path_b_points_pixel_.emplace_back(x, y);
      }
      return;
    }

    // 使用随机贝塞曲线路径
    int control_x1 = path_b_start_pixel_.x + (rand() % 200 - 100);
    int control_y1 = path_b_start_pixel_.y + (rand() % 200 - 100);
    int control_x2 = path_b_end_pixel_.x + (rand() % 200 - 100);
    int control_y2 = path_b_end_pixel_.y + (rand() % 200 - 100);

    // 三次贝塞尔曲线
    for (int i = 1; i <= steps; ++i) {
      double t = (double)i / steps;

      // 三次贝塞尔曲线公式
      double x = (1 - t) * (1 - t) * (1 - t) * path_b_start_pixel_.x + 3 * (1 - t) * (1 - t) * t * control_x1 +
                 3 * (1 - t) * t * t * control_x2 + t * t * t * path_b_end_pixel_.x;

      double y = (1 - t) * (1 - t) * (1 - t) * path_b_start_pixel_.y + 3 * (1 - t) * (1 - t) * t * control_y1 +
                 3 * (1 - t) * t * t * control_y2 + t * t * t * path_b_end_pixel_.y;

      path_b_points_pixel_.emplace_back((int)x, (int)y);
    }
  }

  std::vector<Point> cvt_pixels_to_meters(const std::vector<PointPixel>& pixels) {
    std::vector<Point> points;
    for (const auto& pixel : pixels) points.emplace_back(cvt_pixel_to_meter(pixel));
    return points;
  }

  Point cvt_pixel_to_meter(const PointPixel& pixel) {
    // 将像素坐标转换为米（假设中心为0,0）
    double x = (pixel.x - 600) / scale_factor_;  // 居中变换
    double y = (400 - pixel.y) / scale_factor_;  // Y轴翻转
    return Point(x, y);
  }

  PointPixel cvt_meter_to_pixel(const Point& pt) {
    int x = static_cast<int>(pt.x * scale_factor_ + 600);
    int y = static_cast<int>(400 - pt.y * scale_factor_);
    return PointPixel(x, y);
  }

  void calculate_cross_point() {
    if (path_a_points_pixel_.size() < 2 || path_b_points_pixel_.size() < 2) {
      return;
    }

    std::vector<Point> path_a_meters = cvt_pixels_to_meters(path_a_points_pixel_);
    std::vector<Point> path_b_meters = cvt_pixels_to_meters(path_b_points_pixel_);

    bool found = false;
    cross_point_meter_ = paths_calculator_ptr_->findLastCrossPoint(path_a_meters, path_b_meters, found);

    if (found) {
      cross_point_pixel_ = cvt_meter_to_pixel(cross_point_meter_);
      is_calculated_ = true;
    } else {
      is_calculated_ = false;
    }

    updateDisplay();
  }

 private:
  void reset() {
    path_a_points_pixel_.clear();
    path_b_points_pixel_.clear();
    is_path_b_ready_ = false;
    is_calculated_ = false;
    draw_mode_ = ModeDrawPathA;
    selection_mode_ = SelectStart;
    canvas_.setTo(cv::Scalar(255, 255, 255));
    updateDisplay();
  }

  void updateDisplay() {
    canvas_.setTo(cv::Scalar(255, 255, 255));

    std::function<void(const cv::Point2i&, cv::Scalar)> draw_coords = [&](const cv::Point2i& pt, cv::Scalar scalar) {
      char text[100];
      const auto& pt_meter = cvt_pixel_to_meter(PointPixel(pt.x, pt.y));
      snprintf(text, sizeof(text), "(%.2f, %.2f)", pt_meter.x, pt_meter.y);
      cv::Point2i text_pos(pt.x + 15, pt.y - 15);
      cv::putText(canvas_, text, text_pos, cv::FONT_HERSHEY_SIMPLEX, 1.0, scalar, 1);
    };

    // 绘制路径A（红色）
    if (!path_a_points_pixel_.empty()) {
      for (size_t i = 1; i < path_a_points_pixel_.size(); ++i) {
        cv::Point2i pt1(path_a_points_pixel_[i - 1].x, path_a_points_pixel_[i - 1].y);
        cv::Point2i pt2(path_a_points_pixel_[i].x, path_a_points_pixel_[i].y);
        cv::line(canvas_, pt1, pt2, cv::Scalar(0, 0, 255), 2);
      }

      // 如果路径已选择，画出闭合线
      if (draw_mode_ != ModeDrawPathA && path_a_points_pixel_.size() > 2) {
        cv::Point2i pt1(path_a_points_pixel_.back().x, path_a_points_pixel_.back().y);
        cv::Point2i pt2(path_a_points_pixel_[0].x, path_a_points_pixel_[0].y);
        cv::line(canvas_, pt1, pt2, cv::Scalar(0, 0, 255), 2);
      }
    }

    // 绘制当前正在绘制的点
    if (!path_a_points_pixel_.empty()) {
      for (const auto& pt : path_a_points_pixel_) {
        cv::Point2i point(pt.x, pt.y);
        cv::circle(canvas_, point, 5, cv::Scalar(0, 0, 255), -1);
        draw_coords(point, cv::Scalar(0, 0, 255));
      }
    }

    // 绘制路径B（绿色）
    if (!path_b_points_pixel_.empty()) {
      for (size_t i = 1; i < path_b_points_pixel_.size(); ++i) {
        cv::Point2i pt1(path_b_points_pixel_[i - 1].x, path_b_points_pixel_[i - 1].y);
        cv::Point2i pt2(path_b_points_pixel_[i].x, path_b_points_pixel_[i].y);
        cv::line(canvas_, pt1, pt2, cv::Scalar(0, 255, 0), 2);
      }

      // PathB起点终点标记
      cv::Point2i pt_start(path_b_start_pixel_.x, path_b_start_pixel_.y);
      cv::Point2i pt_end(path_b_end_pixel_.x, path_b_end_pixel_.y);
      cv::circle(canvas_, pt_start, 8, cv::Scalar(255, 0, 0), -1);  // 蓝色起点
      cv::circle(canvas_, pt_end, 8, cv::Scalar(0, 165, 255), -1);  // 橙色终点
      draw_coords(pt_start, cv::Scalar(255, 0, 0));
      draw_coords(pt_end, cv::Scalar(0, 165, 255));
    }

    // 绘制交叉点（黑色）
    if (is_calculated_) {
      cv::Point2i pt_cross(cross_point_pixel_.x, cross_point_pixel_.y);
      cv::circle(canvas_, pt_cross, 10, cv::Scalar(0, 0, 0), -1);
      cv::circle(canvas_, pt_cross, 5, cv::Scalar(255, 255, 255), -1);

      char text[100];
      snprintf(text, sizeof(text), "Cross: (%.2f, %.2f)", cross_point_meter_.x, cross_point_meter_.y);
      cv::Point2i text_pos(cross_point_pixel_.x + 15, cross_point_pixel_.y - 15);
      cv::putText(canvas_, text, text_pos, cv::FONT_HERSHEY_SIMPLEX, 1.0, cv::Scalar(0, 0, 255), 2);
    }

    // 显示当前模式
    std::string mode_text;
    switch (draw_mode_) {
      case ModeDrawPathA:
        mode_text = "Mode: Draw Path A (click points, middle-click to close)";
        break;
      case ModeSelectPoints:
        mode_text = "Mode: Select Path B points (click start and end)";
        break;
    }

    cv::Point2i pos_mode(10, 30);
    cv::putText(canvas_, mode_text, pos_mode, cv::FONT_HERSHEY_SIMPLEX, 0.6, cv::Scalar(255, 0, 0), 1);

    if (selection_mode_ == SelectStart && draw_mode_ == ModeSelectPoints) {
      cv::Point2i pos_text(10, 60);
      cv::putText(canvas_, "Click first point for Path B", pos_text, cv::FONT_HERSHEY_SIMPLEX, 0.6,
                  cv::Scalar(255, 0, 0), 1);
    } else if (selection_mode_ == SelectEnd && draw_mode_ == ModeSelectPoints) {
      cv::Point2i pos_text(10, 60);
      cv::putText(canvas_, "Click second point for Path B", pos_text, cv::FONT_HERSHEY_SIMPLEX, 0.6,
                  cv::Scalar(255, 0, 0), 1);
    }

    cv::imshow(window_name_.c_str(), canvas_);
  }

 private:
  cv::Mat canvas_;
  std::string window_name_ = "Path Cross Point Simulation";

  DrawingMode draw_mode_;
  SelectMode selection_mode_;

  PathsCrossPoints::Ptr paths_calculator_ptr_ = std::make_shared<PathsCrossPoints>();

  double scale_factor_ = 1.f;

  std::vector<PointPixel> path_a_points_pixel_;
  std::vector<PointPixel> path_b_points_pixel_;

  PointPixel path_b_start_pixel_;
  PointPixel path_b_end_pixel_;

  Point cross_point_meter_;
  PointPixel cross_point_pixel_;

  bool is_path_b_ready_;
  bool is_calculated_;
};

}  // namespace mapping

int main() {
  mapping::PathSimulation sim;
  sim.run();
  return 0;
}