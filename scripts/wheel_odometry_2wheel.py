#!/usr/bin/env python
# -*- coding: utf-8 -*-
# code for python2.7import rospy

import rospy
import serial
import time
import signal
import sys
import tf
import math
from nav_msgs.msg import Odometry
from wheel_odometry.msg import Encoder_2wheel

# global parameters to store old encoder information
g_last_encoder_left = 0
g_last_encoder_right = 0
g_last_time = 0

# global parameters to store last wheel odometry
g_last_robot_location = [0.0] * 3  # [x,y,theta] theta isn't used perhaps
g_last_robot_velocity = [0.0] * 2  # [linear_vel, angular_vel]
g_last_robot_orientation = [0.0] * 4  # [x,y,z,w], at quaternion

# constants for wheel odometry of the robot
PULSE_PER_ROUND = 0.0  # pulse per a round of the wheel
WHEEL_DIAMETER = 0.0  # wheel diameter of the robot[m] : 6 inch
TREAD = 0.0  # tread width of the robot[m]

# other global parameters
g_odometry_counts = 0


def set_parameters():
    global PULSE_PER_ROUND, WHEEL_DIAMETER, TREAD
    PULSE_PER_ROUND = rospy.get_param('~pulse_per_round', 723.24)
    WHEEL_DIAMETER = rospy.get_param('~wheel_diameter', 0.1524)
    TREAD = rospy.get_param('~tread', 0.289)
    if PULSE_PER_ROUND == 0 or WHEEL_DIAMETER == 0 or TREAD == 0:
        rospy.logwarn(
            "if you haven't set ros parameter indicates /pulse_per_round, /wheel_diameter, and /tread, Please command '$rosparam set /***' or set them in a launch file")
    else:
        rospy.loginfo("you have set output pulse per wheel round : " + str(PULSE_PER_ROUND) + " [ppr]")
        rospy.loginfo("you have set diameter of the wheel : " + str(WHEEL_DIAMETER) + " [m]")
        rospy.loginfo("you have set tread(distanse between two wheels) of your robot : " + str(TREAD) + " [m]")
    print("")


def callback_calculate_odometry(encoder_2wheel):
    global g_last_encoder_left, g_last_encoder_right, g_last_time

    # subscribe encoder data and store them
    encoder_left = encoder_2wheel.left_encoder
    encoder_right = encoder_2wheel.right_encoder

    # calculate time that passed since last loop to calculate velocity
    current_time = time.time()
    delta_t = current_time - g_last_time
    g_last_time = current_time

    # calculate odometry data
    wheel_odometry_data = calculate_odometry(encoder_left, encoder_right,
                                             g_last_encoder_left, g_last_encoder_right, delta_t)
    # store message to topic
    store_to_topic(wheel_odometry_data)

    # publish topic for odometry
    wheel_odometry_2wheel_pub.publish(wheel_odometry_2wheel)

    # store last encoder data
    g_last_encoder_left = encoder_left
    g_last_encoder_right = encoder_right


def calculate_odometry(enc_L, enc_R, last_enc_L, last_enc_R, dt):
    global g_last_robot_location, g_last_robot_velocity
    global PULSE_PER_ROUND, TREAD, WHEEL_DIAMETER

    # parameters for robot location[x,y,theta] & robot velocity[linear, angular]
    # and robot orientation[x,y,z,w] at quaternion
    current_robot_location = [0.0] * 3
    current_robot_velocity = [0.0] * 2
    current_robot_orientation = [0.0] * 4

    # calculate wheels' or robot's movement
    # difference of encoder count from last loop
    delta_encoder_left = enc_L - last_enc_L
    delta_encoder_right = enc_R - last_enc_R
    # calculate wheel distance since last loop
    delta_distance_left = (delta_encoder_left /
                           PULSE_PER_ROUND) * math.pi * WHEEL_DIAMETER
    delta_distance_right = (delta_encoder_right /
                            PULSE_PER_ROUND) * math.pi * WHEEL_DIAMETER
    # calculate wheel velocity
    wheel_velocity_left = delta_distance_left / dt
    wheel_velocity_right = delta_distance_right / dt

    # calculate current location of the robot
    # calculate location : theta[rad]
    current_robot_location[2] = g_last_robot_location[2] + \
        (delta_distance_right - delta_distance_left) / TREAD
    # calculate mean value of robot's heading
    heading_mean = (current_robot_location[2] + g_last_robot_location[2]) / 2
    # calculate location : x[m]
    current_robot_location[0] = g_last_robot_location[0] + \
        ((delta_distance_left + delta_distance_right) / 2) * \
        math.cos(heading_mean)
    # calculate location : y[m]
    current_robot_location[1] = g_last_robot_location[1] + \
        ((delta_distance_left + delta_distance_right) / 2) * \
        math.sin(heading_mean)

    # calculate current robot velocity
    # calculate linear velocity[m/s]
    current_robot_velocity[0] = (
        wheel_velocity_left + wheel_velocity_right) / 2
    # calculate angular velocity[rad/s]
    current_robot_velocity[1] = (
        wheel_velocity_right - wheel_velocity_left) / TREAD

    # calculate current robot orientation
    current_robot_orientation = tf.transformations.quaternion_from_euler(
        0, 0, current_robot_location[2])

    # store data as last data
    g_last_robot_location = current_robot_location

    # merge all data to single 1 * 9 vector
    odometry_data = current_robot_location
    odometry_data.extend(current_robot_velocity)
    odometry_data.extend(current_robot_orientation)
    return odometry_data


def store_to_topic(odometry_data_toStore):
    global g_odometry_counts

    wheel_odometry_2wheel.header.seq = g_odometry_counts
    wheel_odometry_2wheel.pose.pose.position.x = odometry_data_toStore[0]
    wheel_odometry_2wheel.pose.pose.position.y = odometry_data_toStore[1]
    wheel_odometry_2wheel.twist.twist.linear.x = odometry_data_toStore[3]
    wheel_odometry_2wheel.twist.twist.angular.z = odometry_data_toStore[4]
    wheel_odometry_2wheel.pose.pose.orientation.x = odometry_data_toStore[5]
    wheel_odometry_2wheel.pose.pose.orientation.y = odometry_data_toStore[6]
    wheel_odometry_2wheel.pose.pose.orientation.z = odometry_data_toStore[7]
    wheel_odometry_2wheel.pose.pose.orientation.w = odometry_data_toStore[8]
    g_odometry_counts = g_odometry_counts + 1


if __name__ == '__main__':
    # initialize node as "mcu_interface"
    rospy.init_node('wheel_odometry_2wheel')

    # publisher to inform current PID gains
    wheel_odometry_2wheel_pub = rospy.Publisher(
        'wheel_odometry_2wheel', Odometry, queue_size=1, latch=True)
    wheel_odometry_2wheel = Odometry()
    wheel_odometry_2wheel.header.frame_id = 'map'
    wheel_odometry_2wheel.child_frame_id = 'frame'

    # subscribe encoder information and call function to calculate odometry
    rospy.Subscriber('encoder_2wheel', Encoder_2wheel,
                     callback_calculate_odometry)

    # set parameters : configuration of your robots
    set_parameters()

    # start running node
    # callback function that calculate odometry and publish it will executed -
    # every after this node subscribed encoder information
    rospy.spin()
