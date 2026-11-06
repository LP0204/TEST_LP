"""Subscribe to camera images and display them with OpenCV."""

import cv2
import rclpy
from cv_bridge import CvBridge, CvBridgeError
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import Image


class CameraRGB(Node):
    def __init__(self):
        super().__init__('camera_rgb')
        self.bridge = CvBridge()
        self.sub_cam = self.create_subscription(
            Image, '/image_rgb', self.cam_callback,
            QoSProfile(
                depth=10,
                reliability=ReliabilityPolicy.RELIABLE,
                durability=DurabilityPolicy.VOLATILE))

    def cam_callback(self, msg):
        try:
            cv_img = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        except CvBridgeError as error:
            self.get_logger().error(str(error))
            return
        cv2.imshow('Image window', cv_img)
        cv2.waitKey(3)


def main(args=None):
    rclpy.init(args=args)
    node = CameraRGB()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        cv2.destroyAllWindows()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
