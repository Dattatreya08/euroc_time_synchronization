import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
import cv2
from cv_bridge import CvBridge
import csv
import os

class CameraPlayer(Node):
    def __init__(self):
        super().__init__('camera_player')
        
        self.declare_parameter('dataset_path', '/root/docker_ws/datasets/euroc/MH_01_easy/MH_01_easy/mav0/cam0')
        self.declare_parameter('topic', '/camera/image')
        self.declare_parameter('frequency', 20.0)
        
        self.dataset_path = self.get_parameter('dataset_path').value
        self.bridge = CvBridge()
        self.publisher = self.create_publisher(Image, self.get_parameter('topic').value, 10)
        
        csv_path = os.path.join(self.dataset_path, 'data.csv')
        self.data = []
        with open(csv_path, 'r') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                self.data.append((int(row[0]), row[1].strip()))  # Keep as int
        
        self.index = 0
        period = 1.0 / self.get_parameter('frequency').value
        self.timer = self.create_timer(period, self.publish_frame)
        self.get_logger().info(f'CameraPlayer loaded {len(self.data)} frames')

    def publish_frame(self):
        if self.index >= len(self.data):
            self.get_logger().info('Camera replay completed')
            return
            
        ts_ns, filename = self.data[self.index]
        img_path = os.path.join(self.dataset_path, 'data', filename)
        
        cv_img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)  # Grayscale
        if cv_img is None:
            self.get_logger().warn(f'Image load failed: {filename}')
            self.index += 1
            return
        
        msg = self.bridge.cv2_to_imgmsg(cv_img, encoding='mono8')
        
        # FIXED Timestamp (nanoseconds to sec/nsec)
        msg.header.stamp.sec = ts_ns // 1_000_000_000
        msg.header.stamp.nanosec = ts_ns % 1_000_000_000
        msg.header.frame_id = 'cam0'
        
        self.publisher.publish(msg)
        self.index += 1

def main(args=None):
    rclpy.init(args=args)
    node = CameraPlayer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
