import rclpy
from rclpy.node import Node
import time

class HelloWorldNode(Node):
    def __init__(self, name):
        super().__init__(name)
        while rclpy.ok():
            self.get_logger().info("Hello World")
            time.sleep(0.5)

def main(args=None):
    rclpy.init(args=args)
    node = HelloWorldNode("node_helloworld_class")

    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()