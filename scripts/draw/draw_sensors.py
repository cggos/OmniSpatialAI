#!/usr/bin/env python
# coding=utf-8

import numpy as np
import matplotlib.pyplot as plt

if_imu = "/home/ghc/projects/slam_results/2025-03-06-13-57-17/sensor/imu.txt"
if_rtk = "/home/ghc/projects/slam_results/2025-03-06-13-57-17/sensor/rtk.txt"

imu = np.loadtxt(if_imu)
rtk = np.loadtxt(if_rtk)

t = imu[:, 0]
acc = imu[:, 1:4]
acc_norms = np.linalg.norm(acc, axis=1)

rtk_type = rtk[:, 0]
rtk_time = rtk[:, 1]

vel_e_rtk = rtk[:, 8]
vel_n_rtk = rtk[:, 9]
vel_g_rtk = rtk[:, 10]

plt.figure()
plt.plot(rtk_time, vel_e_rtk, 'r', label='vel_e_rtk')
plt.plot(rtk_time, vel_n_rtk, 'g', label='vel_n_rtk')
plt.plot(rtk_time, vel_g_rtk, 'b', label='vel_g_rtk')
plt.title('velocity')
plt.axis('equal')
plt.legend(loc='upper right')

plt.figure()
# plt.plot(t, acc[:, 0], 'r', label='acc_x')
plt.plot(t, acc[:, 1], 'g', label='acc_y')
# plt.plot(t, acc[:, 2], 'b', label='acc_z')
plt.plot(t, acc_norms, 'b', label='acc_norm')
plt.title('Acc')
plt.legend()

plt.figure()
plt.plot(rtk_time, rtk_type, 'r.', label='rtk type')
plt.title('RTK')
plt.legend()

plt.show()
