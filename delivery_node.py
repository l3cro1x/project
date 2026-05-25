cat << 'EOF' > scripts/delivery_node.py
#!/usr/bin/env python3
import rospy
import math
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from delivery_sim.srv import Order, OrderResponse

class DeliveryRobot:
    def __init__(self):
        rospy.init_node('delivery_courier_node')
        
        self.current_x = 0.0
        self.current_y = 0.0
        self.current_theta = 0.0
        
        self.pose_sub = rospy.Subscriber('/turtle1/pose', Pose, self.pose_callback)
        self.cmd_pub = rospy.Publisher('/turtle1/cmd_vel', Twist, queue_size=10)
        
        self.srv = rospy.Service('order_pizza', Order, self.handle_delivery_request)
        rospy.loginfo("Курьер готов принимать заказы через сервис 'order_pizza'!")

    def pose_callback(self, msg):
        self.current_x = msg.x
        self.current_y = msg.y
        self.current_theta = msg.theta

    def handle_delivery_request(self, req):
        rospy.loginfo(f"Получен заказ на точку: X={req.x}, Y={req.y}")
        if not (0 <= req.x <= 11 and 0 <= req.y <= 11):
            return OrderResponse(success=False, message="Точка доставки вне зоны обслуживания!")

        rate = rospy.Rate(10)
        move_cmd = Twist()

        while not rospy.is_shutdown():
            distance = math.sqrt((req.x - self.current_x)**2 + (req.y - self.current_y)**2)
            angle_to_target = math.atan2(req.y - self.current_y, req.x - self.current_x)
            
            if distance < 0.2:
                break
                
            angle_error = angle_to_target - self.current_theta
            angle_error = math.atan2(math.sin(angle_error), math.cos(angle_error))

            if abs(angle_error) > 0.2:
                move_cmd.linear.x = 0.0
                move_cmd.angular.z = 2.0 * angle_error
            else:
                move_cmd.linear.x = 1.5 * distance
                move_cmd.angular.z = 1.0 * angle_error
                
            self.cmd_pub.publish(move_cmd)
            rate.sleep()

        move_cmd.linear.x = 0.0
        move_cmd.angular.z = 0.0
        self.cmd_pub.publish(move_cmd)

        return OrderResponse(success=True, message="Пицца успешно доставлена!")

if __name__ == '__main__':
    try:
        robot = DeliveryRobot()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
EOF
