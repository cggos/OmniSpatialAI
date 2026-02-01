#pragma once

#include <algorithm>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <opencv2/core/core.hpp>
#include <opencv2/features2d/features2d.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <string>
#include <vector>

#if defined(WITH_DBOW2) && defined(WITH_DBOW3)
#undef WITH_DBOW3
#endif

#if not defined(WITH_DBOW2) && not defined(WITH_DBOW3)
#define WITH_DBOW2
#endif

#ifdef WITH_DBOW2
#include "DBoW2/FORB.h"
#include "DBoW2/TemplatedVocabulary.h"
typedef DBoW2::TemplatedVocabulary<DBoW2::FORB::TDescriptor, DBoW2::FORB> ORBVocabulary;
using namespace DBoW2;
#endif

#ifdef WITH_DBOW3
#include <DBoW3/DBoW3.h>
using namespace DBoW3;
#endif

using namespace cv;
using namespace std;

// #define DATA_TUM
const int MAX_NUM = 500;

std::vector<std::string> load_paths(const std::string& data_dir) {
  vector<string> rgb_files;
#ifndef DATA_TUM
  // read all .png files in the directory and store their absolute paths
  namespace fs = std::filesystem;
  if (!fs::exists(data_dir) || !fs::is_directory(data_dir)) {
    cout << "data directory does not exist or is not a directory: " << data_dir << endl;
    return {};
  }

  for (const auto& entry : fs::directory_iterator(data_dir)) {
    if (!entry.is_regular_file()) continue;
    auto path = entry.path();
    auto ext = path.extension().string();
    if (ext == ".png" || ext == ".PNG") {
      rgb_files.push_back(fs::absolute(path).string());
    }
  }
  // keep deterministic ordering
  sort(rgb_files.begin(), rgb_files.end());
#else
  ifstream fin(data_dir + "/associate.txt");
  if (!fin) {
    cout << "please generate the associate file called associate.txt!" << endl;
    return {};
  }
  vector<string> depth_files;
  vector<double> rgb_times, depth_times;
  while (!fin.eof()) {
    string rgb_time, rgb_file, depth_time, depth_file;
    fin >> rgb_time >> rgb_file >> depth_time >> depth_file;
    rgb_times.push_back(atof(rgb_time.c_str()));
    depth_times.push_back(atof(depth_time.c_str()));
    rgb_files.push_back(data_dir + "/" + rgb_file);
    depth_files.push_back(data_dir + "/" + depth_file);
    if (fin.good() == false) break;
  }
  fin.close();
#endif
  return rgb_files;
}

std::vector<Mat> comput_orb_descs(const std::string& data_dir) {
  vector<string> rgb_files = load_paths(data_dir);

  cout << "generating features ... " << endl;
  vector<Mat> descriptors;
  Ptr<Feature2D> detector = ORB::create();
  int index = 1;
  for (const string& rgb_file : rgb_files) {
    Mat image = imread(rgb_file);
    if (image.empty()) continue;
    
    vector<KeyPoint> keypoints;
    Mat descriptor;
    detector->detectAndCompute(image, Mat(), keypoints, descriptor);
    if(descriptor.empty()) continue;

    descriptors.push_back(descriptor);
    cout << "extracting features from image " << index++ << endl;
    if (index > MAX_NUM) break;
  }
  cout << "descriptors size: " << descriptors.size() << " features." << endl;

  return descriptors;
}

std::vector<cv::Mat> to_descriptor_vector(const cv::Mat& Descriptors) {
  std::vector<cv::Mat> vDesc;
  vDesc.reserve(Descriptors.rows);
  for (int j = 0; j < Descriptors.rows; j++) vDesc.push_back(Descriptors.row(j));
  return vDesc;
}
