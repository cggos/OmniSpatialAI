#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import math
import matplotlib.pyplot as plt

# pip install pymap3d
import pymap3d as pm

fi = open(
    "/opt/user_data/dms/dataset_company/slamtec_aurora/bj_outdoor/with_rtk_01/sensor_rtk_20251121084054.txt",
    'r',
)
fo = open(
    "/opt/user_data/dms/dataset_company/slamtec_aurora/bj_outdoor/with_rtk_01/sensor_rtk_20251121084054_enu.tum",
    'w',
)


def nmea_deg_to_decimal(nmea_deg: float) -> float:
    """
    将 NMEA 格式的经纬度 (DDMM.MMMM 或 DDDMM.MMMM) 转换为十进制度 (Decimal Degrees).
    例如:
        纬度 3954.8765 -> 39 + 54.8765/60 = 39.914608°
        经度 11623.4567 -> 116 + 23.4567/60 = 116.390945°
    参数:
        nmea_deg (float): NMEA 标准格式的经纬度，如 3954.8765（纬度）或 11623.4567（经度）
    返回:
        float: 十进制度表示的地理坐标
    """
    degrees = int(nmea_deg / 100)
    minutes = nmea_deg - degrees * 100
    decimal_deg = degrees + minutes / 60.0
    return decimal_deg


def lla_to_enu(
    lat: float, lon: float, h: float, lat0: float, lon0: float, h0: float
) -> tuple:
    """
    将 LLA 坐标 (lat, lon, h) 转换为以 (lat0, lon0, h0) 为原点的 ENU 局部坐标（单位：米）
    参数:
        lat, lon: 当前点纬度、经度（十进制度，+北/-南, +东/-西）
        h: 当前点椭球高（m）
        lat0, lon0: 原点纬度、经度（十进制度）
        h0: 原点椭球高（m）
    返回:
        (east, north, up): 在原点建立的 ENU 坐标系下的坐标（单位：米）
    """
    # WGS84 椭球参数
    a = 6378137.0  # 长半轴
    f = 1 / 298.257223563
    e2 = 2 * f - f * f  # 第一偏心率平方
    # 转弧度
    phi = math.radians(lat)
    lam = math.radians(lon)
    phi0 = math.radians(lat0)
    lam0 = math.radians(lon0)
    dphi = phi - phi0
    dlam = lam - lam0
    dh = h - h0
    # 计算 sin/cos 提高效率
    sin_phi0 = math.sin(phi0)
    cos_phi0 = math.cos(phi0)
    # N: 卯酉圈曲率半径 (prime vertical radius)
    N = a / math.sqrt(1 - e2 * sin_phi0**2)
    # M: 子午圈曲率半径 (meridional radius)
    M = a * (1 - e2) / (1 - e2 * sin_phi0**2) ** 1.5
    # ENU 计算（一阶线性近似）
    east = (N + h) * cos_phi0 * dlam
    north = (M + h) * dphi
    up = dh
    return (east, north, up)


n = 0
xx = []
yy = []
for line in fi:
    global lon0, lat0, alt0
    data = line.split(' ')

    # status = int(data[1])
    # if status != 4:
    #     continue

    timestamp = float(data[0])  # UTC time in seconds
    lon = float(data[2])
    lat = float(data[3])
    alt = float(data[4])

    timestamp = f"{timestamp:.8f}"
    lon = nmea_deg_to_decimal(lon)
    lat = nmea_deg_to_decimal(lat)

    if n == 0:
        lon0, lat0, alt0 = lon, lat, alt
        print(f"origin set to: ({lon0}, {lat0}, {alt0})")

    res = pm.geodetic2enu(lat, lon, alt, lat0, lon0, alt0)

    xx.append(res[0])
    yy.append(res[1])
    fo.write(
        ("{} {} {} {} {} {} {} {}\n").format(
            timestamp, res[0], res[1], res[2], 0, 0, 0, 1
        )
    )
    # print(res)
    n += 1

print(f"total points : {n}")
print("output to file:", fo.name)

fi.close()
fo.close()

plt.plot(xx, yy)

plt.show()
