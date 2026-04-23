# RK SoC Benchmark

---

## Overview

```bash
ps -ef | grep <keyword-of-process-name>
ps -efL | grep <keyword-of-process-name> # display threads

ps -p <PID> -T # display threads

top
top -p <PID>
top -p <PID> -H # display threads
```


## RK3588

### CPU

四核 A55 分别是 cpu0、cpu1、cpu2、cpu3; 四核 A76 分别是 cpu5、cpu6、cpu7、cpu8。
此过程以 cpu0 为例操作,实际过程 cpu1、cpu2、cpu3 会同时改变; 单独操作 cpu4、 cpu5、
cpu6、cpu7 相互之间不会受到影响。

CPU0: 

```bash
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_available_governors
# conservative ondemand userspace powersave performance schedutil

cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_available_frequencies
# 408000 600000 816000 1008000 1200000 1416000

cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor # schedutil

cat /sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_cur_freq # 1008000


echo userspace > /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor

echo 1800000 > /sys/devices/system/cpu/cpu0/cpufreq/scaling_setspeed
```

### GPU

```bash
cat /sys/class/devfreq/fb000000.gpu/governor # simple_ondemand
cat /sys/class/devfreq/fb000000.gpu/cur_freq # 300000000
cat /sys/class/devfreq/fb000000.gpu/load # 0@300000000Hz

# or /sys/devices/platform/fb000000.gpu/devfreq/fb000000.gpu/xxx

cat /sys/kernel/debug/clk/clk_gpu/clk_rate # 198000000

cat /sys/kernel/debug/mali0/gpu_memory # mali0  0
```

### NPU

```bash
cat /sys/class/devfreq/fdab0000.npu/available_frequencies
# 300000000 400000000 500000000 600000000 700000000 800000000

cat /sys/class/devfreq/fdab0000.npu/available_governors
# rknpu_ondemand dmc_ondemand userspace powersave performance simple_ondemand

cat /sys/class/devfreq/fdab0000.npu/governor # rknpu_ondemand
cat /sys/class/devfreq/fdab0000.npu/cur_freq # 800000000
cat /sys/class/devfreq/fdab0000.npu/load # 100@800000000Hz

# or /sys/devices/platform/fdab0000.npu/devfreq/fdab0000.npu/xxx

cat /sys/kernel/debug/clk/clk_npu_dsu0/clk_rate # 250000000
cat /sys/kernel/debug/rknpu/load
```

### Memory / DDR


### ISP



### Temp

```bash
cat /sys/class/thermal/thermal_zone0/temp
```
