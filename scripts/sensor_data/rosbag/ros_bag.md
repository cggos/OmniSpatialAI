# ROS Bag 

---

## ROS Bag Splitting

```bash
# e.g.
rosbag filter xxx.bag out.bag "t.to_sec() > 1712932797.964417 and t.to_sec() < 1712932808.9"
```
