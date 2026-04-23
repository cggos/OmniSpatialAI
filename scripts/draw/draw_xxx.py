#!/usr/bin/env python
# coding=utf-8

import numpy as np
import matplotlib.pyplot as plt


data_root = "/home/ghc/projects/slam_results/2025-03-06-13-57-17/"

ss_rtk = np.loadtxt(data_root + "/sensor/rtk.txt")
ss_whl = np.loadtxt(data_root + "/sensor/whl.txt")
sai_vio_l = np.loadtxt(data_root + '/sai_sai/sai_vio_l.txt', delimiter=',')

rtk_type = ss_rtk[:, 0]
t_rtk = ss_rtk[:, 1]
vel_e_rtk = ss_rtk[:, 8] / 3.6
vel_n_rtk = ss_rtk[:, 9] / 3.6
vel_g_rtk = ss_rtk[:, 10] / 3.6

t_whl = ss_whl[:, 0]
v_whl = ss_whl[:, 1]

t_vio_l = sai_vio_l[:, 0]
v_vio_l = sai_vio_l[:, 8:11]

plt.figure()
plt.plot(t_rtk, vel_g_rtk, label='v_rtk')
plt.plot(t_whl, v_whl, label='v_whl')
plt.plot(t_vio_l, v_vio_l[:, 0], label='vx_vio')
plt.title('velocity')
plt.legend(loc='upper right')

# plt.figure()
# plt.plot(rtk_time, rtk_type, 'r.', label='rtk type')
# plt.title('RTK')
# plt.legend()

plt.show()
