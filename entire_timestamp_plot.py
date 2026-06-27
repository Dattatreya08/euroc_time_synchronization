import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, Imu
from synchronization_msgs.msg import SyncedPair
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from collections import deque
import time

class EntireTimestampPlot(Node):
    def __init__(self):
        super().__init__('entire_timestamp_plot')
        self.camera_ts = deque(maxlen=1000)
        self.imu_ts = deque(maxlen=5000)
        self.synced_pairs = deque(maxlen=1000)  # (cam_ts, imu_ts, diff)
        
        self.create_subscription(Image, '/camera/image', self.camera_cb, 10)
        self.create_subscription(Imu, '/imu/data', self.imu_cb, 10)
        self.create_subscription(SyncedPair, '/synchronized_pair', self.sync_cb, 10)
        
        self.last_save = time.time()
        self.get_logger().info('Entire Timestamp Plot started')

    def camera_cb(self, msg):
        ts = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        self.camera_ts.append(ts)

    def imu_cb(self, msg):
        ts = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        self.imu_ts.append(ts)

    def sync_cb(self, msg):
        c = msg.camera_timestamp.sec + msg.camera_timestamp.nanosec * 1e-9
        i = msg.imu_timestamp.sec + msg.imu_timestamp.nanosec * 1e-9
        d = msg.time_difference * 1000
        self.synced_pairs.append((c, i, d))

    def save_plot(self):
        plt.figure(figsize=(16, 12))
        
        # 1. All Timestamps
        plt.subplot(3, 1, 1)
        plt.plot(list(self.camera_ts), [2]*len(self.camera_ts), 'b.', label='Camera', markersize=8)
        plt.plot(list(self.imu_ts), [1]*len(self.imu_ts), 'r.', label='IMU', markersize=4, alpha=0.5)
        plt.title('All Timestamps (Camera & IMU)')
        plt.yticks([1,2], ['IMU', 'Camera'])
        plt.legend()
        plt.grid(True)
        
        # 2. Synced Pairs
        plt.subplot(3, 1, 2)
        for c, i, d in list(self.synced_pairs)[-500:]:
            plt.plot([c, i], [2, 1], 'g-', alpha=0.7)
            plt.plot(c, 2, 'b.', markersize=8)
            plt.plot(i, 1, 'r.', markersize=6)
        plt.title('Synced Pairs (Green lines = Matched Camera-IMU)')
        plt.yticks([1,2], ['IMU', 'Camera'])
        plt.grid(True)
        
        # 3. Time Difference
        plt.subplot(3, 1, 3)
        diffs = [d for _,_,d in list(self.synced_pairs)[-500:]]
        if diffs:
            plt.plot(diffs, 'g.-')
            plt.axhline(y=5, color='r', linestyle='--', label='5ms')
        plt.title('Time Difference (ms)')
        plt.legend()
        plt.grid(True)
        
        plt.tight_layout()
        plt.savefig('entire_timestamp_analysis.png', dpi=200)
        plt.close()
        self.get_logger().info('Entire timestamp plot saved: entire_timestamp_analysis.png')

    def timer_callback(self):
        if time.time() - self.last_save > 3:
            self.save_plot()
            self.last_save = time.time()

def main():
    rclpy.init()
    node = EntireTimestampPlot()
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
