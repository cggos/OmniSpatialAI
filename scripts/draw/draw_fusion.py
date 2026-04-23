import numpy as np
import matplotlib.pyplot as plt

file_path = '/tmp/'

fusion = np.loadtxt(file_path + 'sai_fusion.txt')
odom = np.genfromtxt(file_path + 'sai_sai.ms', delimiter=',')
odom_fusion = np.loadtxt(file_path + 'sai_odom.txt')
rtk = np.loadtxt(file_path + 'sai_rtk.txt')

t_f = fusion[:, 0]
p_f = fusion[:, 1:4]
yaw_f = fusion[:, 8]
pitch_f = fusion[:, 9]
roll_f = fusion[:, 10]

t_o = odom[:, 0] * 1e-9
p_o = odom[:, 1:4]
yaw_o = odom[:, 18]
q_o = odom[:, 18:21]
v_o = odom[:, 8:11]
bg = odom[:, 11:14]
ba = odom[:, 14:17]
td = odom[:, 17]

p_o_fusion = odom_fusion[:, 1:4]

t_rtk = rtk[:, 0]
p_rtk = rtk[:, 1:4]
yaw_rtk = rtk[:, 8]

plt.figure()
plt.plot(p_f[:, 0], p_f[:, 1], 'b.')
plt.plot(p_rtk[:, 0], p_rtk[:, 1], 'r.')
plt.plot(p_o_fusion[:, 0], p_o_fusion[:, 1], 'g.')
plt.title('xy-fusion')
plt.axis('equal')

plt.figure()
plt.plot(t_f, yaw_f, label='Yaw Fusion')
plt.plot(t_rtk, yaw_rtk, label='Yaw RTK')
plt.plot(t_o, yaw_o, label='Yaw Odom')
plt.title('yaw')
plt.legend()

plt.figure()
plt.plot(t_o, yaw_o * 180 / np.pi)
plt.title('yaw_odom')

plt.show()
