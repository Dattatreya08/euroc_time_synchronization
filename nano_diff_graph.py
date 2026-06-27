import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, Imu
from synchronization_msgs.msg import SyncedPair
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from collections import deque
import time

class NanoDiffGraph(Node):
    def __init__(self):
        super().__init__('nano_diff_graph')
        self.camera_events = deque(maxlen=500)
        self.imu_events = deque(maxlen=2000)
        self.synced_events = deque(maxlen=500)
        
        self.create_subscription(Image, '/camera/image', self.camera_cb, 10)
        self.create_subscription(Imu, '/imu/data', self.imu_cb, 10)
        self.create_subscription(SyncedPair, '/synchronized_pair', self.sync_cb, 10)
        
        self.last_save = time.time()
        self.get_logger().info('Nano-second level graph started')

    def camera_cb(self, msg):
        ts = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        self.camera_events.append(ts)

    def imu_cb(self, msg):
        ts = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        self.imu_events.append(ts)

    def sync_cb(self, msg):
        ts = msg.camera_timestamp.sec + msg.camera_timestamp.nanosec * 1e-9
        self.synced_events.append(ts)

    def save_graph(self):
        plt.figure(figsize=(16, 8))
        
        # Vertical lines for events
        if self.camera_events:
            plt.vlines(list(self.camera_events), 1.8, 2.2, color='blue', linewidth=2, label='Camera')
        if self.imu_events:
            plt.vlines(list(self.imu_events), 0.8, 1.2, color='red', linewidth=0.5, alpha=0.6, label='IMU')
        if self.synced_events:
            plt.vlines(list(self.synced_events), 0.8, 2.2, color='green', linewidth=1.5, label='Synced')
        
        plt.title('Nano-Second Level Event Timeline\nBlue = Camera | Red = IMU | Green = Synced')
        plt.xlabel('Time (seconds)')
        plt.yticks([1, 2], ['IMU Level', 'Camera Level'])
        plt.legend()
        plt.grid(True, axis='x')
        
        plt.tight_layout()
        plt.savefig('nano_diff_graph.png', dpi=200)
        plt.close()
        self.get_logger().info('Nano-second graph saved: nano_diff_graph.png')

    def timer_callback(self):
        if time.time() - self.last_save > 3:
            self.save_graph()
            self.last_save = time.time()

def main():
    rclpy.init()
    node = NanoDiffGraph()
    node.create_timer(2.0, node.timer_callback)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.save_graph()
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
