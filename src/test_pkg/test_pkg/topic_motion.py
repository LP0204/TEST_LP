"""按课件执行原地踏步 3 秒、前进 5 秒、随后停止的运动示例。"""

import math
import signal
import time

from protocol.msg import MotionServoCmd
import rclpy
from rclpy.node import Node


class BasicMove(Node):
    """通过 10 Hz 的运动话题控制机器狗。"""

    def __init__(self, name='topic_motion'):
        """读取名字空间和速度参数，并创建发布者与定时器。"""
        super().__init__(name)
        self.declare_parameter('dog_name', 'fixed_value')
        self.declare_parameter('forward_speed', 0.1)
        self.dog_name = self.get_parameter('dog_name').value.strip('/')
        self.forward_speed = float(self.get_parameter('forward_speed').value)
        if not self.dog_name:
            raise ValueError('dog_name 不能为空，请填写机器狗实际的名字空间。')
        if (not math.isfinite(self.forward_speed) or
                not 0.0 <= self.forward_speed <= 0.65):
            raise ValueError('forward_speed 必须在 0.0 到 0.65 m/s 之间。')

        self.topic_name = '/{}/motion_servo_cmd'.format(self.dog_name)
        self.pub = self.create_publisher(MotionServoCmd, self.topic_name, 10)
        self.start_time = None
        self.phase = None
        self.timer = self.create_timer(0.1, self.timer_callback)
        self.get_logger().info('运动话题：{}'.format(self.topic_name))

    def log_phase(self, phase, message):
        """仅在阶段发生变化时打印日志。"""
        if self.phase != phase:
            self.phase = phase
            self.get_logger().info(message)

    def timer_callback(self):
        """按经过的时间发布踏步、前进或结束指令。"""
        if self.start_time is None:
            # 等订阅者出现后再计时，避免发现连接时丢失前几秒的指令。
            if self.pub.get_subscription_count() == 0:
                self.log_phase('waiting', '等待运动话题的订阅者，请核对 dog_name。')
                return
            self.start_time = time.monotonic()

        elapsed = time.monotonic() - self.start_time
        if elapsed >= 8.0:
            # 结束帧会停止伺服运动；仅把速度清零仍可能保持原地踏步。
            self.publish_stop()
            self.log_phase('stopped', '8 秒已到，已发送结束帧；按 Ctrl+C 退出。')
            return

        msg = MotionServoCmd()
        msg.motion_id = 303                # 慢速行走，与课件一致
        msg.cmd_type = 1                   # Data：持续运动数据帧
        msg.value = 2                      # 垂直步态
        msg.step_height = [0.05, 0.05]     # 抬腿高度 5 cm

        if elapsed < 3.0:
            msg.vel_des = [0.0, 0.0, 0.0]
            self.log_phase('stepping', '0–3 秒：原地踏步。')
        else:
            msg.vel_des = [self.forward_speed, 0.0, 0.0]
            self.log_phase(
                'walking',
                '3–8 秒：向前行走，速度 {} m/s。'.format(self.forward_speed))

        self.pub.publish(msg)

    def publish_stop(self):
        """发送结束帧，并明确将期望速度置零。"""
        msg = MotionServoCmd()
        msg.motion_id = 303
        msg.cmd_type = 2                   # End：结束运动，不是 Data 帧
        msg.vel_des = [0.0, 0.0, 0.0]
        self.pub.publish(msg)

    def stop_motion(self):
        """取消定时器，并在退出前连续发送三次结束帧。"""
        self.timer.cancel()
        if self.start_time is not None and rclpy.ok():
            for _ in range(3):
                self.publish_stop()
                time.sleep(0.1)


def main(args=None):
    """启动节点，并在 Ctrl+C 时先发送结束帧再关闭 ROS。"""
    rclpy.init(args=args)
    # 由 Python 先处理 Ctrl+C，使结束帧能在 ROS 上下文关闭前发送。
    previous_sigint = signal.signal(signal.SIGINT, signal.default_int_handler)
    node = None
    try:
        node = BasicMove()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        try:
            if node is not None:
                try:
                    node.stop_motion()
                finally:
                    node.destroy_node()
        finally:
            try:
                if rclpy.ok():
                    rclpy.shutdown()
            finally:
                signal.signal(signal.SIGINT, previous_sigint)


if __name__ == '__main__':
    main()
