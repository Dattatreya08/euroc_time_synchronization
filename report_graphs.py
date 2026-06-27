import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, Imu
from synchronization_msgs.msg import SyncedPair
import matplotlib.pyplot as plt
from collections import deque
import time
import numpy as np

class ReportGraphs(Node):
    def __init__(self):
        super().__init__('report_graphs')
        self.camera_ts = deque(maxlen=1000)
        self.imu_ts = deque(maxlen=5000)
        self.diffs = deque(maxlen=1000)
        
        self.create_subscription(Image, '/camera/image', self.camera_cb, 10)
        self.create_subscription(Imu, '/imu/data', self.imu_cb, 10)
        self.create_subscription(SyncedPair, '/synchronized_pair', self.sync_cb, 10)
        
        self.get_logger().info('Report graphs generator started')

    def camera_cb(self, msg):
        ts = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        self.camera_ts.append(ts)

    def imu_cb(self, msg):
        ts = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        self.imu_ts.append(ts)

    def sync_cb(self, msg):
        diff = msg.time_difference * 1000
        self.diffs.append(diff)

    def generate_graphs(self):
        plt.style.use('default')
        fig = plt.figure(figsize=(16, 14))
        
        # Graph 1: Timeline
        plt.subplot(3, 2, 1)
        plt.plot(list(self.camera_ts), [1]*len(self.camera_ts), 'b|', label='Camera 20Hz')
        plt.plot(list(self.imu_ts), [0]*len(self.imu_ts), 'r|', label='IMU 200Hz', alpha=0.5)
        plt.title('Graph 1: Sensor Timeline')
        plt.yticks([0,1], ['IMU', 'Camera'])
        plt.legend()
        plt.grid(True)
        
        # Graph 2: Time Difference
        plt.subplot(3, 2, 2)
        plt.plot(list(self.diffs), 'g.-')
        plt.axhline(y=5, color='r', linestyle='--')
        plt.title('Graph 2: Synchronization Error')
        plt.ylabel('ms')
        plt.grid(True)
        
        # Graph 3: Histogram
        plt.subplot(3, 2, 3)
        plt.hist(list(self.diffs), bins=50, color='purple', alpha=0.7)
        plt.axvline(x=5, color='r', linestyle='--')
        plt.title('Graph 3: Error Histogram')
        plt.xlabel('Time Difference (ms)')
        plt.grid(True)
        
        plt.tight_layout()
        plt.savefig('report_graphs.png', dpi=200)
        plt.close()
        self.get_logger().info('Report graphs saved: report_graphs.png')

def main():
    rclpy.init()
    node = ReportGraphs()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.generate_graphs()
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
