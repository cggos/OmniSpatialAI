# CPU Affinity

---

```bash
# get
taskset -pc <PID>

# set
taskset -pc <cpu-list> <PID>  # cpu-list: 0 0,2  1,2,3
taskset -c <cpu-list> <process-name>  # 不能实现各个线程绑定不同核心，该命令只能支持到进程级别
```
