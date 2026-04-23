#!/bin/sh

printf "\n1. 项目成员数量："
git log --pretty='%aN' | sort -u | wc -l

printf "\n\n2. 按用户名统计代码提交次数：\n\n"
printf "%10s  %s\n" "次数" "用户名"
git log --pretty='%aN' | sort | uniq -c | sort -k1 -n -r | head -n 5
printf "\n%10s" "合计"
printf "\n%5s" ""
git log --oneline | wc -l

printf "\n3. 按用户名统计代码提交行数：\n\n"
printf "%15s %20s+ %20s- %18s\n" "用户名" "总行数" "添加行数" "删除行数"
git log --format='%aN' | sort -u -r | while read name; do
	printf "%15s" "$name"
	git log --author="$name" --pretty=tformat: --numstat \
		":(exclude)app/ros1/src/sensors" \
		":(exclude)app/ros1/src/vision_opencv" \
		":(exclude)include/vp_vol/aruco_detector.h" \
		":(exclude)include/vp_vol/aruco_marker.h" \
		":(exclude)include/vp_vol/aruco_marker_info.h" \
		":(exclude)include/vp_vol/corner_refinement.h" \
		":(exclude)include/vp_vol/quadrilateral.h" \
		":(exclude)include/vp_vol/square_finder.h" \
		":(exclude)src/aruco_detector.cpp" \
		":(exclude)src/aruco_marker.cpp" \
		":(exclude)src/aruco_marker_info.cpp" \
		":(exclude)src/corner_refinement.cpp" \
		":(exclude)src/quadrilateral.cpp" \
		":(exclude)src/square_finder.cpp" \
		":(exclude)src/trt/" \
		":(exclude)include/vp_sem/yolov5_trt/" |
		awk '{ add += $1; subs += $2; loc += $1 - $2 } END { printf "%15s %15s %15s \n", loc, add, subs }' \
			-
done

printf "\n%15s   " "总计："
git log --pretty=tformat: --numstat |
	awk '{ add += $1; subs += $2; loc += $1 - $2 } END { printf "%15s %15s %15s \n", loc, add, subs }'

echo ""
# shellcheck disable=SC2162
# read -n 1 -p "请按任意键继续..."
