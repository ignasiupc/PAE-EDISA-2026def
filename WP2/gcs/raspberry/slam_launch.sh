#!/usr/bin/env bash
# Launch LiDAR driver + SLAM Toolbox on Raspberry Pi.
# Tested with ROS2 Jazzy + rplidar_ros / ydlidar_ros2_driver.
#
# Usage:
#   ./slam_launch.sh                        # RPLiDAR on /dev/ttyUSB0
#   ./slam_launch.sh --port /dev/ttyUSB1    # different port
#   ./slam_launch.sh --lidar ydlidar        # YDLIDAR X4/G4
#   ./slam_launch.sh --map /tmp/my_map      # load existing map (localization mode)

LIDAR="unitree"
PORT="/dev/ttyUSB0"
BAUD=115200
FRAME="unilidar_lidar"   # frame del L1 (cambia a "laser" si usas RPLiDAR)
MAP_FILE=""
PARAMS_DIR="$(dirname "$(realpath "$0")")"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --lidar) LIDAR="$2";    shift 2 ;;
    --port)  PORT="$2";     shift 2 ;;
    --baud)  BAUD="$2";     shift 2 ;;
    --map)   MAP_FILE="$2"; shift 2 ;;
    *) echo "Unknown arg: $1"; shift ;;
  esac
done

source /opt/ros/jazzy/setup.bash
source ~/rosbridge_ws/install/setup.bash 2>/dev/null || true

# Give serial port access without sudo each time
sudo chmod 666 "$PORT" 2>/dev/null || true

echo "[SLAM] driver=$LIDAR  port=$PORT  baud=$BAUD"

# ── LiDAR driver ──────────────────────────────────────────────────────────────
if [ "$LIDAR" = "unitree" ]; then
  # Unitree L1 4D — conecta por Ethernet (Pi: 192.168.1.50, LiDAR: 192.168.1.62)
  # Asegura IP en la interfaz ethernet (ajusta eth0 si es otro nombre)
  sudo ip addr add 192.168.1.50/24 dev eth0 2>/dev/null || true

  source ~/unitree_lidar_ros2/install/setup.bash 2>/dev/null || true

  ros2 launch unitree_lidar_ros2 launch.py &
  LIDAR_PID=$!
  sleep 3

  # Convierte PointCloud2 (/unilidar/cloud) → LaserScan (/scan) para SLAM Toolbox
  # Corte horizontal ±5 cm alrededor del plano del LiDAR
  ros2 run pointcloud_to_laserscan pointcloud_to_laserscan_node \
    --ros-args \
    -r __ns:=/ \
    -r /cloud_in:=/unilidar/cloud \
    -p target_frame:=unilidar_lidar \
    -p transform_tolerance:=0.01 \
    -p min_height:=-0.05 \
    -p max_height:=0.05 \
    -p angle_min:=-3.14159 \
    -p angle_max:=3.14159 \
    -p angle_increment:=0.00872 \
    -p scan_time:=0.033 \
    -p range_min:=0.1 \
    -p range_max:=30.0 \
    -p use_inf:=true &
  PC2LS_PID=$!

elif [ "$LIDAR" = "rplidar" ]; then
  ros2 run rplidar_ros rplidar_composition \
    --ros-args \
    -p serial_port:="$PORT" \
    -p serial_baudrate:=$BAUD \
    -p frame_id:="$FRAME" \
    -p angle_compensate:=true \
    -p scan_mode:=Standard &
  LIDAR_PID=$!

elif [ "$LIDAR" = "ydlidar" ]; then
  ros2 run ydlidar_ros2_driver ydlidar_ros2_driver_node \
    --ros-args \
    -p port:="$PORT" \
    -p baudrate:=$BAUD \
    -p frame_id:="$FRAME" \
    -p lidar_type:=1 \
    -p device_type:=6 &
  LIDAR_PID=$!

elif [ "$LIDAR" = "hokuyo" ]; then
  ros2 run urg_node urg_node_driver \
    --ros-args -p serial_port:="$PORT" -p frame_id:="$FRAME" &
  LIDAR_PID=$!

else
  echo "[SLAM] Unknown lidar type '$LIDAR'. Start it manually."
  LIDAR_PID=""
fi

sleep 2

# ── TF estáticos ─────────────────────────────────────────────────────────────
# base_link → frame del LiDAR (ajusta x y z a la posición física en el dron)
ros2 run tf2_ros static_transform_publisher \
  --frame-id base_link --child-frame-id "$FRAME" \
  --x 0 --y 0 --z 0.1 --roll 0 --pitch 0 --yaw 0 &
TF_SENSOR_PID=$!

# odom → base_link: usa MAVROS si está activo; si no (prueba en banco),
# publica un TF estático (el dron "no se mueve" en odom pero SLAM compensa con scan matching)
if ! ros2 topic list 2>/dev/null | grep -q "/mavros/local_position/odom"; then
  echo "[SLAM] MAVROS no detectado — usando TF estático odom→base_link (prueba en tierra)"
  ros2 run tf2_ros static_transform_publisher \
    --frame-id odom --child-frame-id base_link \
    --x 0 --y 0 --z 0 --roll 0 --pitch 0 --yaw 0 &
  TF_ODOM_PID=$!
fi

# ── SLAM Toolbox ──────────────────────────────────────────────────────────────
if [ -n "$MAP_FILE" ]; then
  # Localization mode: load existing map
  echo "[SLAM] Localization mode — map: $MAP_FILE"
  ros2 launch slam_toolbox localization_launch.py \
    slam_params_file:="$PARAMS_DIR/slam_params.yaml" \
    map_file_name:="$MAP_FILE" \
    use_sim_time:=false &
else
  # Mapping mode: build new map
  echo "[SLAM] Mapping mode"
  ros2 launch slam_toolbox online_async_launch.py \
    slam_params_file:="$PARAMS_DIR/slam_params.yaml" \
    use_sim_time:=false &
fi
SLAM_PID=$!

echo "[SLAM] Running — lidar PID=$LIDAR_PID  slam PID=$SLAM_PID"
echo "       Topics: /scan → SLAM Toolbox → /map + /slam_toolbox/pose"
echo "       GCS subscribes automatically when connected to rosbridge."
echo "       Press Ctrl+C to stop."

trap "kill $LIDAR_PID $SLAM_PID 2>/dev/null" EXIT INT TERM
wait
