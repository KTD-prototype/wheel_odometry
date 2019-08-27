# wheel_odometry
## Package Overview
A simple ROS package to publish wheel odometry data for differential 2-wheel driven robot such as Roomba.<br>
This package will subscribe encoder count from left/right motor、and publish odometry data as native ROS message ***nav_msgs/Odometry***
<br>
<br>
<br>

## Sample Video
Here's sample video, using self balanced robot (inverted pendelum)
You can also view data at RVIZ.
<br>
<br>
<br>

## Operating Environment
Confirmed environments are as follows:
  * Ubuntu16.04
  * python2.7.12
  * ROS kinetic kame <br>
  * Gear motor w/ encoder：[servo city](https://www.servocity.com/317-rpm-spur-gear-motor-w-encoder)
<br>
<br>
<br>

## Installation
(assume that you are working at workspace : ***catkin_ws*** )<br>
`   $ cd ~/catkin_ws/src`<br>
`   $ git clone git@github.com:KTD-prototype/wheel_odometry.git`<br>
`   $ cd ~/catkin_ws`<br>
`   $ catkin_make`
<br>
<br>
<br>


## How To Use
### Used Message Type
Encoder message (to subscribe)<br>
  * /Encoder_2wheel<br>
    - int64 left_encoder<br>
    - int64 right_encoder<br>
<br>
Odometry message (to publish)<br>
  *[nav_msgs/Odometry](http://docs.ros.org/melodic/api/nav_msgs/html/msg/Odometry.html)<br>

### Subscribe Encoder
This package will subscribe message type : ***Encoder_2wheel*** composed of ***left_encoder*** & ***right_encoder*** , and calculate wheel odometry.<br>
To use, set your robot control node to publish L/R encoder information as ***Encoder_2wheel*** type message.<br>
When you run ***scripts/wheel_odometry_2wheel.py*** and your robot's node to publish encoder info, this module will subscribe encoder information, calculate and publish ***nav_msgs/Odometry*** .<br>


### Parameters
  * ***~/pulse_per_round*** : The number of pulses that your encoder generates per a wheel rotation [pulse/round]. By default, it is set as 723.24 [pulse/round] for author's robot.
  * ***~/wheel_diameter*** : Diameter of your robot's wheel[m]. By default, it is set as 0.1524 [m] (6inches) for author's robot.
  * ***~/tread*** : Distance between your robot's L/R wheel[m]. By default, it is set as 0.289 [m] for author's robot.
