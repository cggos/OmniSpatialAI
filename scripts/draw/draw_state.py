#!/usr/bin/env python
# coding=utf-8

import numpy as np
import matplotlib.pyplot as plt

data_root = "/tmp/sai_data/2025-03-13-14-41-01/"

data_dir = data_root + '/sai_sai/'

sai_rtk = np.loadtxt(data_dir + 'sai_rtk.txt')
sai_fusion = np.loadtxt(data_dir + 'sai_fusion.txt')
sai_vio_g = np.genfromtxt(data_dir + 'sai_vio_g.txt')
sai_vio_l = np.loadtxt(data_dir + 'sai_vio_l.txt', delimiter=',')

t_rtk = sai_rtk[:, 0]
p_rtk = sai_rtk[:, 1:4]
yaw_rtk = sai_rtk[:, 8]

t_f = sai_fusion[:, 0]
p_f = sai_fusion[:, 1:4]
yaw_f = sai_fusion[:, 8]
pitch_f = sai_fusion[:, 9]
roll_f = sai_fusion[:, 10]

t_vio_g = sai_vio_g[:, 0]
p_vio_g = sai_vio_g[:, 1:4]
yaw_vio_g = sai_vio_g[:, 8]

t_vio_l = sai_vio_l[:, 0]
p_vio_l = sai_vio_l[:, 1:4]
v_vio_l = sai_vio_l[:, 8:11]
bg_vio_l = sai_vio_l[:, 11:14]
ba_vio_l = sai_vio_l[:, 14:17]
td_vio_l = sai_vio_l[:, 17]

# Odom
plt.figure()
plt.plot(p_rtk[:, 0], p_rtk[:, 1], 'r-', label='rtk')
plt.plot(p_f[:, 0], p_f[:, 1], 'g-', label='fusion')
# plt.plot(p_vio_g[:, 0], p_vio_g[:, 1], 'b-', label='vio_g')
# plt.plot(p_vio_l[:, 0], p_vio_l[:, 1], 'b-', label='vio_l')
plt.title('Fusion Odom')
plt.axis('equal')
plt.legend(loc='upper right')

plt.figure()
plt.plot(p_vio_l[:, 0], p_vio_l[:, 1], 'b-', label='vio_l')
plt.title('VIO Odom')
plt.axis('equal')
plt.legend(loc='upper right')

# Yaw
# plt.figure()
# plt.plot(t_f, yaw_f * 180 / np.pi, 'g', label='yaw_fusion')
# plt.plot(t_rtk, yaw_rtk * 180 / np.pi, 'r', label='yaw_rtk')
# plt.plot(t_vio_g, yaw_vio_g * 180 / np.pi, 'b', label='yaw_vio_g')
# plt.title('yaw')
# plt.legend()

# XY-Time
# plt.figure()
# plt.plot(t_rtk, p_rtk[:, 0], label='px_rtk')
# plt.plot(t_rtk, p_rtk[:, 1], label='py_rtk')
# plt.plot(t_f, p_f[:, 0], label='px_fusion')
# plt.plot(t_f, p_f[:, 1], label='py_fusion')
# plt.title('RTK & Fusion XY')
# plt.legend()

# Vel
# plt.figure()
# plt.plot(t_vio_l, v_vio_l[:, 0], 'r', label='vx')
# plt.plot(t_vio_l, v_vio_l[:, 1], 'g', label='vy')
# plt.plot(t_vio_l, v_vio_l[:, 2], 'b', label='vz')
# plt.title('velocity')
# plt.legend()

# Td & Bias
# fig, ax = plt.subplots(3, 1)
# fig.suptitle("motion state of VP-SAI")
# plt.subplot(311)
# plt.plot(t_vio_l, td_vio_l, 'r', label="td_ic")
# plt.ylabel("td_ic")
# plt.legend(loc='upper right')
# plt.subplot(312)
# plt.plot(t_vio_l, ba_vio_l[:, 0], 'r', label="bax")
# plt.plot(t_vio_l, ba_vio_l[:, 1], 'g', label="bay")
# plt.plot(t_vio_l, ba_vio_l[:, 2], 'b', label="baz")
# plt.ylabel("ba")
# plt.legend(loc='upper right')
# plt.subplot(313)
# plt.plot(t_vio_l, bg_vio_l[:, 0], 'r--', label="bgx")
# plt.plot(t_vio_l, bg_vio_l[:, 1], 'g--', label="bgy")
# plt.plot(t_vio_l, bg_vio_l[:, 2], 'b--', label="bgz")
# plt.ylabel("bg")
# plt.legend(loc='upper right')
# # plt.xticks(np.arange(min(x), max(x)+1, 10.0))
# plt.xlabel("timestamp (s)")

plt.show()
