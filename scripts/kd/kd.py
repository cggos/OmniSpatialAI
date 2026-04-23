#!/usr/bin/env python
# coding=utf-8

import numpy as np

a  = np.array([[-1, 0, 0], [0, 1, 0], [0, 0, -1]])
print(a)

b= np.array([0.05143, -0.00453, -0.01503])

print(b)
print(np.dot(a, b))

print(np.linalg.inv(a))

print(np.linalg.pinv(a))

A = np.matrix(a)
print(A.I)


