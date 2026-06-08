#!/usr/bin/env python3
"""
Boustrophedon (lawnmower) full coverage planner.

Generates a dense sweep-line path over all free cells of /map and publishes
it as nav_msgs/Path to /move_base/TebLocalPlannerROS/global_plan.
coverage_pursuit.py drives the robot along the path.

Row-to-row transitions use BFS through free cells so the path never
crosses unknown or obstacle space (i.e. never leaves the map/track area).

ROS parameters (~):
  sweep_spacing (float, default 0.6): spacing between sweep lines [m]
  safety_margin (float, default 0.30): obstacle inflation radius [m]
  path_step     (float, default 0.15): sampling step along rows and BFS paths [m]
  start_delay   (float, default 3.0):  seconds before publishing
"""

from collections import deque

import numpy as np
import rospy
from scipy.ndimage import binary_dilation
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import OccupancyGrid, Path
from tf.transformations import quaternion_from_euler


class BoustrophedonPlanner:
    def __init__(self):
        self.sweep_spacing = rospy.get_param('~sweep_spacing', 0.8)
        self.safety_margin = rospy.get_param('~safety_margin', 0.30)
        self.path_step     = rospy.get_param('~path_step',     0.15)
        self.start_delay   = rospy.get_param('~start_delay',   3.0)

        self._map_msg  = None
        self._map_sub  = rospy.Subscriber('/map', OccupancyGrid, self._map_cb, queue_size=1)
        self._path_pub = rospy.Publisher(
            '/move_base/TebLocalPlannerROS/global_plan', Path,
            queue_size=1, latch=True)

    # ------------------------------------------------------------------

    def _map_cb(self, msg):
        self._map_msg = msg
        self._map_sub.unregister()

    def _navigable_grid(self):
        info = self._map_msg.info
        h, w = info.height, info.width
        data = np.array(self._map_msg.data, dtype=np.int8).reshape(h, w)
        free     = (data == 0)
        occupied = (data == 100)
        pad = max(1, int(self.safety_margin / info.resolution))
        return free & ~binary_dilation(occupied, iterations=pad), info

    def _to_world(self, row, col, info):
        x = info.origin.position.x + (col + 0.5) * info.resolution
        y = info.origin.position.y + (row + 0.5) * info.resolution
        return float(x), float(y)

    # ------------------------------------------------------------------
    # BFS/transition helpers

    _BFS_NEIGHBORS = [(-1, 0), (1, 0), (0, -1), (0, 1)]   # 4-connectivity

    def _bfs_path(self, navigable, start_rc, end_rc):
        """
        Return ordered list of (row, col) from start_rc to end_rc through
        navigable cells.  Returns [] if not connected.
        """
        h, w  = navigable.shape
        start = (int(start_rc[0]), int(start_rc[1]))
        end   = (int(end_rc[0]),   int(end_rc[1]))

        if start == end:
            return [start]
        if not navigable[start[0], start[1]]:
            rospy.logwarn("BFS: start %s not navigable", start)
            return []
        if not navigable[end[0], end[1]]:
            rospy.logwarn("BFS: end %s not navigable", end)
            return []

        queue  = deque([start])
        parent = {start: None}

        while queue:
            r, c = queue.popleft()
            if (r, c) == end:
                path, node = [], (r, c)
                while node is not None:
                    path.append(node)
                    node = parent[node]
                path.reverse()
                return path
            for dr, dc in self._BFS_NEIGHBORS:
                nb = (r + dr, c + dc)
                if (0 <= nb[0] < h and 0 <= nb[1] < w
                        and navigable[nb[0], nb[1]]
                        and nb not in parent):
                    parent[nb] = (r, c)
                    queue.append(nb)

        return []

    def _transition_path(self, restricted, navigable, start_rc, end_rc):
        """
        Find a transition path that avoids sweep rows whenever possible.

        'restricted' is the navigable mask with all sweep-row cells set to False.
        The BFS uses restricted so transitions travel through inter-sweep space
        (no crossings with sweep lines).  If no restricted path exists, falls
        back to full-navigable BFS (crossings may occur but no path is lost).
        """
        h, w  = restricted.shape
        start = (int(start_rc[0]), int(start_rc[1]))
        end   = (int(end_rc[0]),   int(end_rc[1]))

        if start == end:
            return [start]
        if not navigable[start[0], start[1]] or not navigable[end[0], end[1]]:
            return []

        # Phase 1 — BFS through restricted space (sweep rows blocked).
        # The end cell is always allowed even if it sits on a sweep row.
        queue  = deque([start])
        parent = {start: None}

        while queue:
            r, c = queue.popleft()
            if (r, c) == end:
                path, node = [], (r, c)
                while node is not None:
                    path.append(node)
                    node = parent[node]
                path.reverse()
                return path
            for dr, dc in self._BFS_NEIGHBORS:
                nb = (r + dr, c + dc)
                nr, nc = nb
                if (0 <= nr < h and 0 <= nc < w
                        and (restricted[nr, nc] or nb == end)
                        and navigable[nr, nc]
                        and nb not in parent):
                    parent[nb] = (r, c)
                    queue.append(nb)

        # Phase 2 — fall back: allow sweep rows (crossings may occur)
        return self._bfs_path(navigable, start, end)

    # ------------------------------------------------------------------

    @staticmethod
    def _find_segments(row_navigable):
        """Return [(start_col, end_col), ...] for each contiguous free segment."""
        cols = np.where(row_navigable)[0]
        if len(cols) == 0:
            return []
        segs, s, p = [], int(cols[0]), int(cols[0])
        for c in cols[1:]:
            c = int(c)
            if c > p + 1:
                segs.append((s, p))
                s = c
            p = c
        segs.append((s, p))
        return segs

    def _generate_xy(self, navigable, info):
        """
        Returns ordered list of (x, y) world-coordinate points.

        Each sweep row is split into contiguous free-cell segments; the robot
        sweeps each segment independently, alternating direction row by row.
        Transitions between segments use _transition_path, which routes through
        inter-sweep-row space so the path does not cross other sweep lines.
        """
        h, _       = navigable.shape
        sweep_step = max(1, int(self.sweep_spacing / info.resolution))
        col_step   = max(1, int(self.path_step     / info.resolution))
        min_seg    = col_step   # drop segments narrower than one path_step

        # Build a restricted navigable mask used for non-crossing transitions:
        # sweep rows are blocked so the BFS is forced through inter-sweep space.
        restricted = navigable.copy()
        for row in range(sweep_step // 2, h, sweep_step):
            restricted[row, :] = False

        points        = []
        left_to_right = True
        prev_end_rc   = None

        for row in range(sweep_step // 2, h, sweep_step):
            segments = self._find_segments(navigable[row])
            segments = [(lo, hi) for lo, hi in segments if hi - lo + 1 >= min_seg]
            if not segments:
                continue

            if not left_to_right:
                segments = segments[::-1]

            for (c_lo, c_hi) in segments:
                cols = np.arange(c_lo, c_hi + 1)
                if not left_to_right:
                    cols = cols[::-1]
                sampled = cols[::col_step]

                seg_start_rc = (row, int(sampled[0]))
                seg_end_rc   = (row, int(sampled[-1]))

                if prev_end_rc is not None:
                    trans = self._transition_path(
                        restricted, navigable, prev_end_rc, seg_start_rc)
                    if not trans:
                        rospy.logwarn(
                            "Coverage: skipping unreachable segment row=%d cols=%d-%d",
                            row, c_lo, c_hi)
                        continue
                    for rc in trans[1:-1]:
                        points.append(self._to_world(rc[0], rc[1], info))

                for c in sampled:
                    points.append(self._to_world(row, int(c), info))

                prev_end_rc = seg_end_rc

            left_to_right = not left_to_right

        return points

    # ------------------------------------------------------------------

    def _build_path_msg(self, xy):
        path = Path()
        path.header.frame_id = 'map'
        path.header.stamp    = rospy.Time.now()

        n   = len(xy)
        yaw = 0.0
        for i, (x, y) in enumerate(xy):
            if i + 1 < n:
                dx  = xy[i + 1][0] - x
                dy  = xy[i + 1][1] - y
                yaw = np.arctan2(dy, dx)
            q  = quaternion_from_euler(0.0, 0.0, yaw)
            ps = PoseStamped()
            ps.header          = path.header
            ps.pose.position.x = x
            ps.pose.position.y = y
            ps.pose.orientation.x = q[0]
            ps.pose.orientation.y = q[1]
            ps.pose.orientation.z = q[2]
            ps.pose.orientation.w = q[3]
            path.poses.append(ps)

        return path

    # ------------------------------------------------------------------

    def run(self):
        rospy.loginfo("Coverage planner: waiting for /map ...")
        while not rospy.is_shutdown() and self._map_msg is None:
            rospy.sleep(0.5)
        if rospy.is_shutdown():
            return

        rospy.loginfo("Coverage planner: generating path (after %.1f s) ...",
                      self.start_delay)
        rospy.sleep(self.start_delay)

        navigable, info = self._navigable_grid()
        free_count = int(navigable.sum())
        rospy.loginfo("Coverage planner: %d navigable cells", free_count)
        if free_count == 0:
            rospy.logwarn("Coverage planner: no free cells — reduce safety_margin")
            return

        rospy.loginfo("Coverage planner: computing BFS transitions (may take a moment) ...")
        xy = self._generate_xy(navigable, info)
        rospy.loginfo("Coverage planner: %d path points generated", len(xy))
        if not xy:
            rospy.logwarn("Coverage planner: empty path — check sweep_spacing / safety_margin")
            return

        path = self._build_path_msg(xy)
        self._path_pub.publish(path)
        rospy.loginfo(
            "Coverage planner: path published  "
            "(sweep_spacing=%.2f m, %d points)",
            self.sweep_spacing, len(xy))
        rospy.spin()


if __name__ == '__main__':
    rospy.init_node('coverage_planner')
    BoustrophedonPlanner().run()
