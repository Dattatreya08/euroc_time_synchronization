import rclpy
from rclpy.node import Node
from collections import deque
from sensor_msgs.msg import Image, Imu
from synchronization_msgs.msg import SyncedPair

class MessageSynchronizer(Node):
    def __init__(self):
        super().__init__('message_synchronizer')
        
        self.declare_parameter('buffer_duration', 3.0)
        self.declare_parameter('camera_topic', '/camera/image')
        self.declare_parameter('imu_topic', '/imu/data')
        self.declare_parameter('output_topic', '/synchronized_pair')
        
        self.buffer_duration = self.get_parameter('buffer_duration').value
        
        self.camera_buffer = deque(maxlen=1000)
        self.imu_buffer = deque(maxlen=5000)
        
        self.camera_sub = self.create_subscription(
            Image, self.get_parameter('camera_topic').value, self.camera_callback, 10)
        
        self.imu_sub = self.create_subscription(
            Imu, self.get_parameter('imu_topic').value, self.imu_callback, 10)
        
        self.publisher = self.create_publisher(SyncedPair, self.get_parameter('output_topic').value, 10)
        
        self.get_logger().info('Message Synchronizer started with buffer duration = {}s'.format(self.buffer_duration))

    def camera_callback(self, img_msg):
        ts = img_msg.header.stamp.sec + img_msg.header.stamp.nanosec * 1e-9
        self.camera_buffer.append((ts, img_msg))
        self.cleanup_buffers()
        self.try_sync(ts, img_msg)

    def imu_callback(self, imu_msg):
        ts = imu_msg.header.stamp.sec + imu_msg.header.stamp.nanosec * 1e-9
        self.imu_buffer.append((ts, imu_msg))
        self.cleanup_buffers()

    def cleanup_buffers(self):
        if not self.camera_buffer or not self.imu_buffer:
            return
        # Use the latest timestamp in buffer as "now" (dataset time)
        latest_ts = max(self.camera_buffer[-1][0], self.imu_buffer[-1][0])
        cutoff = latest_ts - self.buffer_duration
        
        while self.camera_buffer and self.camera_buffer[0][0] < cutoff:
            self.camera_buffer.popleft()
        while self.imu_buffer and self.imu_buffer[0][0] < cutoff:
            self.imu_buffer.popleft()

    def try_sync(self, cam_ts, cam_msg):
        if not self.imu_buffer:
            return
        
        # Find closest IMU
        closest = min(self.imu_buffer, key=lambda x: abs(x[0] - cam_ts))
        imu_ts, imu_msg = closest
        diff = abs(cam_ts - imu_ts)
        
        pair = SyncedPair()
        pair.header.stamp = self.get_clock().now().to_msg()
        pair.image = cam_msg
        pair.imu = imu_msg
        pair.camera_timestamp = cam_msg.header.stamp
        pair.imu_timestamp = imu_msg.header.stamp
        pair.time_difference = diff
        
        self.publisher.publish(pair)

def main(args=None):
    rclpy.init(args=args)
    node = MessageSynchronizer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
