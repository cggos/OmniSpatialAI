#!/usr/bin/env python
# coding=utf-8

import matplotlib.pyplot as plt

data_root = "/tmp/sai_data/2025-03-01-12-03-57"

file_path = data_root + '/sensor/img.txt'

f1 = open(file_path)

x1 = []
y1 = []
n = 0
m = 0
last_ts = 0

for line in f1:
    if n < 5:
        n += 1
        continue
    data = line.split()
    ts = float(data[0]) * 1e3  # ms
    if last_ts > 0:
        x1.append(m)
        y1.append(ts - last_ts)
        m = m + 1
        if m > 10000:
            break
    last_ts = ts

# plt.plot(x1, y1, 'r--')
plt.scatter(x1, y1)

# plt.xlim(xmin=-5)
# plt.ylim(ymin=-2.5)
# plt.xticks(np.arange(min(x1), max(x1) + 1, 100.0))

# for xy in zip(x, y):
#     plt.annotate("(%s,%s)" % xy, xy=xy, xytext=(-20, 10), textcoords='offset points')
plt.xlabel("frame index")
plt.ylabel("time interval (ms)")
plt.title('time intervals')
plt.legend()

plt.show()
