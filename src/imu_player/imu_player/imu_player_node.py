import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
import csv
import os

class IMUPlayer(Node):
    def __init__(self):
        super().__init__('imu_player')
        
        self.declare_parameter('dataset_path', '/root/docker_ws/datasets/euroc/MH_01_easy/MH_01_easy/mav0/imu0')
        self.declare_parameter('topic', '/imu/data')
        self.declare_parameter('frequency', 200.0)
        
        self.dataset_path = self.get_parameter('dataset_path').value
        self.publisher = self.create_publisher(Imu, self.get_parameter('topic').value, 10)
        
        csv_path = os.path.join(self.dataset_path, 'data.csv')
        self.data = []
        with open(csv_path, 'r') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                ts_ns = int(row[0])
                self.data.append((ts_ns, float(row[1]), float(row[2]), float(row[3]), float(row[4]), float(row[5]), float(row[6])))
        
        self.index = 0
        period = 1.0 / self.get_parameter('frequency').value
        self.timer = self.create_timer(period, self.publish_imu)
        self.get_logger().info(f'IMUPlayer loaded {len(self.data)} measurements')

    def publish_imu(self):
        if self.index >= len(self.data):
            self.get_logger().info('IMU replay completed')
            return
            
        ts_ns, gx, gy, gz, ax, ay, az = self.data[self.index]
        
        msg = Imu()
        
        # FIXED Timestamp (nanoseconds to sec/nsec)
        msg.header.stamp.sec = ts_ns // 1_000_000_000
        msg.header.stamp.nanosec = ts_ns % 1_000_000_000
        msg.header.frame_id = 'imu0'
        
        msg.angular_velocity.x = gx
        msg.angular_velocity.y = gy
        msg.angular_velocity.z = gz
        msg.linear_acceleration.x = ax
        msg.linear_acceleration.y = ay
        msg.linear_acceleration.z = az
        
        # Proper covariance
        msg.angular_velocity_covariance = [0.0001, 0.0, 0.0, 0.0, 0.0001, 0.0, 0.0, 0.0, 0.0001]
        msg.linear_acceleration_covariance = [0.0001, 0.0, 0.0, 0.0, 0.0001, 0.0, 0.0, 0.0, 0.0001]
        
        self.publisher.publish(msg)
        self.index += 1

def main(args=None):
    rclpy.init(args=args)
    node = IMUPlayer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
