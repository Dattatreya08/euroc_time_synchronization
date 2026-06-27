import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, Imu
from synchronization_msgs.msg import SyncedPair
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from collections import deque
import time

class DensityPlot(Node):
    def __init__(self):
        super().__init__('density_plot')
        self.camera_ts = deque(maxlen=2000)
        self.imu_ts = deque(maxlen=20000)  # Larger for IMU
        self.synced_ts = deque(maxlen=2000)
        
        self.create_subscription(Image, '/camera/image', self.camera_cb, 10)
        self.create_subscription(Imu, '/imu/data', self.imu_cb, 10)
        self.create_subscription(SyncedPair, '/synchronized_pair', self.sync_cb, 10)
        
        self.last_save = time.time()
        self.get_logger().info('Density plot started (IMU should have more points)')

    def camera_cb(self, msg):
        ts = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        self.camera_ts.append(ts)

    def imu_cb(self, msg):
        ts = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        self.imu_ts.append(ts)

    def sync_cb(self, msg):
        ts = msg.camera_timestamp.sec + msg.camera_timestamp.nanosec * 1e-9
        self.synced_ts.append(ts)

    def save_plot(self):
        plt.figure(figsize=(16, 10))
        
        # Camera
        plt.subplot(3, 1, 1)
        if self.camera_ts:
            plt.vlines(list(self.camera_ts), 1.8, 2.2, color='blue', linewidth=2, label='Camera (20Hz)')
        plt.title('Camera Events')
        plt.yticks([])
        plt.legend()
        plt.grid(True)
        
        # IMU (should have more lines)
        plt.subplot(3, 1, 2)
        if self.imu_ts:
            plt.vlines(list(self.imu_ts), 0.8, 1.2, color='red', linewidth=0.5, alpha=0.6, label='IMU (200Hz)')
        plt.title('IMU Events (Should be denser)')
        plt.yticks([])
        plt.legend()
        plt.grid(True)
        
        # Synced
        plt.subplot(3, 1, 3)
        if self.synced_ts:
            plt.vlines(list(self.synced_ts), 0.8, 2.2, color='green', linewidth=1.5, label='Synced')
        plt.title('Synced Pairs')
        plt.yticks([])
        plt.legend()
        plt.grid(True)
        
        plt.tight_layout()
        plt.savefig('density_comparison.png', dpi=200)
        plt.close()
        self.get_logger().info('Density plot saved')

    def timer_callback(self):
        if time.time() - self.last_save > 3:
            self.save_plot()
            self.last_save = time.time()

def main():
    rclpy.init()
    node = DensityPlot()
    node.create_timer(2.0, node.timer_callback)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.save_plot()
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
