# Euroc Time Synchronization

ROS 2 Jazzy containerized solution for temporal synchronization of Camera and IMU data from the EuRoC dataset.

## Quick Start using Docker (Recommended)

```bash
# 1. Pull the image from GitHub Container Registry
docker pull ghcr.io/dattatreya08/euroc_time_synchronization:latest

# 2. Run the container (mount your dataset)
docker run --rm -it \
  -v ~/datasets/euroc:/root/docker_ws/datasets/euroc \
  ghcr.io/dattatreya08/euroc_time_synchronization:latest
```

## Author

Nerella Venkatapathi Dattatreya
