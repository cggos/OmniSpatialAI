# sai_tb3_sim

TurtleBot3 Gazebo 仿真包，场景（world）与机器人模型（robot）分离加载。

功能上等价于 `ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py`，但将场景和机器人拆分为独立的 launch 文件，便于在不重启 Gazebo 的前提下更换机器人型号，或在同一场景中加载多个机器人。

## 依赖

| 包 | 用途 |
|---|---|
| `gazebo_ros` | gzserver / gzclient / spawn_entity |
| `turtlebot3_gazebo` | 内置世界文件（.model） |
| `turtlebot3_description` | 机器人 URDF |
| `robot_state_publisher` | 发布 TF 树 |

安装依赖：

```bash
sudo apt install ros-foxy-turtlebot3-gazebo ros-foxy-turtlebot3-description
```

## 构建

```bash
cd <your_ws>
colcon build --packages-select sai_tb3_sim
source install/setup.bash
```

## Launch 文件

```
launch/
├── sim.launch.py     # 主入口：同时启动场景 + 机器人
├── world.launch.py   # 仅启动 Gazebo 场景（gzserver + gzclient）
└── robot.launch.py   # 仅加载机器人（robot_state_publisher + spawn_entity）
```

### sim.launch.py — 主入口

等价于原始的 `turtlebot3_world.launch.py`，内部按顺序包含 `world.launch.py` 和 `robot.launch.py`。

| 参数 | 默认值 | 说明 |
|---|---|---|
| `robot_model` | `burger` | 机器人型号：`burger` \| `waffle` \| `waffle_pi` |
| `world` | turtlebot3_worlds/burger.model | 世界文件完整路径 |
| `x_pose` | `-2.0` | 机器人初始 X 坐标（m） |
| `y_pose` | `-0.5` | 机器人初始 Y 坐标（m） |
| `z_pose` | `0.01` | 机器人初始 Z 坐标（m） |

### world.launch.py — 场景加载

启动 Gazebo 物理服务器和 GUI 客户端。

| 参数 | 默认值 | 说明 |
|---|---|---|
| `world` | turtlebot3_worlds/burger.model | 世界文件完整路径 |
| `verbose` | `false` | 是否开启 Gazebo 详细日志 |

### robot.launch.py — 机器人加载

向运行中的 Gazebo 实例注入机器人，并启动 `robot_state_publisher`。

| 参数 | 默认值 | 说明 |
|---|---|---|
| `robot_model` | `burger` | 机器人型号：`burger` \| `waffle` \| `waffle_pi` |
| `use_sim_time` | `true` | 使用 Gazebo 仿真时钟 |
| `x_pose` | `-2.0` | 初始 X 坐标（m） |
| `y_pose` | `-0.5` | 初始 Y 坐标（m） |
| `z_pose` | `0.01` | 初始 Z 坐标（m） |

## 使用示例

**默认启动（burger + turtlebot3_world）：**

```bash
ros2 launch sai_tb3_sim sim.launch.py
```

**切换机器人型号：**

```bash
ros2 launch sai_tb3_sim sim.launch.py robot_model:=waffle
ros2 launch sai_tb3_sim sim.launch.py robot_model:=waffle_pi
```

**使用自定义世界文件：**

```bash
ros2 launch sai_tb3_sim sim.launch.py world:=/path/to/my_scene.world
```

**同时指定场景和机器人：**

```bash
ros2 launch sai_tb3_sim sim.launch.py robot_model:=waffle world:=/path/to/my_scene.world
```

**仅启动场景（不加载机器人）：**

```bash
ros2 launch sai_tb3_sim world.launch.py
```

**向已运行的 Gazebo 追加机器人（不重启场景）：**

```bash
# 终端 1：先启动场景
ros2 launch sai_tb3_sim world.launch.py

# 终端 2：加载 burger
ros2 launch sai_tb3_sim robot.launch.py robot_model:=burger

# 终端 3：在不同位置再加载 waffle
ros2 launch sai_tb3_sim robot.launch.py robot_model:=waffle x_pose:=1.0 y_pose:=1.0
```

## 与原始包的对比

| | `turtlebot3_gazebo` | `sai_tb3_sim` |
|---|---|---|
| 场景与机器人耦合 | 是（世界文件名含机器人型号） | 否，完全独立 |
| 切换机器人型号 | 需重启整个 launch | 只重启 robot.launch.py |
| 支持多机器人 | 否 | 是（多次调用 robot.launch.py） |
| 自定义世界文件 | 需修改源码 | 命令行参数直接指定 |
| 依赖环境变量 | `TURTLEBOT3_MODEL` 必须设置 | 无需环境变量，参数化控制 |
