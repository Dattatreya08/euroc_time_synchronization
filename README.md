# Euroc Time Synchronization

ROS 2 Jazzy containerized package for temporal synchronization of asynchronous Camera and IMU data from the EuRoC MAV dataset.

## Features
- Configurable sliding buffer window (default: 3.0 seconds)
- Closest timestamp matching between camera frames and IMU measurements
- Non-blocking architecture suitable for high-frequency IMU (100 Hz)
- Publishes synchronized pairs on `/synchronized_pair` topic

## Quick Start (Recommended)

```bash
# Pull the pre-built Docker image
docker pull ghcr.io/dattatreya08/euroc_time_synchronization:latest

# Run the container (mount your EuRoC dataset)
docker run --rm -it \
  -v ~/datasets/euroc:/root/docker_ws/datasets/euroc \
  ghcr.io/dattatreya08/euroc_time_synchronization:latest
```

## Dataset Setup

```bash
mkdir -p ~/datasets/euroc
cd ~/datasets/euroc

wget https://www.research-collection.ethz.ch/bitstreams/7b2419c1-62b5-4714-b7f8-485e5fe3e5fe/download -O MH_01_easy.zip
unzip MH_01_easy.zip
```

## Build from Source (Alternative)

```bash
git clone https://github.com/Dattatreya08/euroc_time_synchronization.git
cd euroc_time_synchronization/sync_ws

source /opt/ros/jazzy/setup.bash
colcon build --symlink-install
source install/setup.bash

ros2 launch message_synchronizer sync.launch.py
```

## Topics

| Topic                | Description                     |
|----------------------|---------------------------------|
| `/camera/image`      | Camera frames                   |
| `/imu/data`          | IMU measurements                |
| `/synchronized_pair` | Synchronized camera + IMU data  |

## Docker Image

```bash
docker pull ghcr.io/dattatreya08/euroc_time_synchronization:latest
```

## Author
Nerella Venkatapathi Dattatreya
```

---

After saving, push it:

```bash
git add README.md
git commit -m "Update README.md"
git push
```

Would you like any changes to this README?
