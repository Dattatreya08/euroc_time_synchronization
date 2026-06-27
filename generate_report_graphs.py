import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, Imu
from synchronization_msgs.msg import SyncedPair
import matplotlib.pyplot as plt
from collections import deque
import time

class ReportGraphs(Node):
    def __init__(self):
        super().__init__('report_graphs')
        self.camera_ts = deque(maxlen=1000)
        self.imu_ts = deque(maxlen=5000)
        self.diffs = deque(maxlen=1000)
        
        self.create_subscription(Image, '/camera/image', self.camera_cb, 10)
        self.create_subscription(Imu, '/imu/data', self.imu_cb, 10)
        self.create_subscription(SyncedPair, '/synchronized_pair', self.sync_cb, 10)
        
        self.get_logger().info('Report Graphs started - saving when data available')

    def camera_cb(self, msg):
        ts = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        self.camera_ts.append(ts)
        self.save_if_ready()

    def imu_cb(self, msg):
        ts = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        self.imu_ts.append(ts)
        self.save_if_ready()

    def sync_cb(self, msg):
        diff = msg.time_difference * 1000
        self.diffs.append(diff)
        self.save_if_ready()

    def save_if_ready(self):
        if len(self.diffs) < 10:
            return
        plt.figure(figsize=(15, 12))
        
        plt.subplot(3, 1, 1)
        plt.plot(list(self.camera_ts), [1]*len(self.camera_ts), 'b|', label='Camera')
        plt.plot(list(self.imu_ts), [0]*len(self.imu_ts), 'r|', label='IMU', alpha=0.5)
        plt.title('Raw Timestamps')
        plt.yticks([0,1], ['IMU', 'Camera'])
        plt.legend()
        
        plt.subplot(3, 1, 2)
        plt.plot(list(self.diffs), 'g.-')
        plt.axhline(y=5, color='r', linestyle='--')
        plt.title('Time Difference (ms)')
        
        plt.subplot(3, 1, 3)
        plt.hist(list(self.diffs), bins=50, color='purple')
        plt.title('Histogram')
        
        plt.tight_layout()
        plt.savefig('assignment_report_graphs.png', dpi=200)
        plt.close()
        self.get_logger().info('Graph saved: assignment_report_graphs.png')

def main():
    rclpy.init()
    node = ReportGraphs()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
