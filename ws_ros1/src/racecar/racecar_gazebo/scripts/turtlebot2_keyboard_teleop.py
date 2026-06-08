#!/usr/bin/env python3
"""Keyboard teleoperation for Turtlebot2.
Publishes geometry_msgs/Twist to /cmd_vel.
Controls: W=forward  S=backward  A=turn left  D=turn right  Q=quit
"""

import signal
from threading import Lock
from tkinter import Frame, Label, Tk

import rospy
from geometry_msgs.msg import Twist

UP    = "w"
LEFT  = "a"
DOWN  = "s"
RIGHT = "d"
QUIT  = "q"

state      = [False, False, False, False]  # [fwd, left, back, right]
state_lock = Lock()
cmd_pub    = None
root       = None

MAX_LINEAR  = 0.5   # m/s
MAX_ANGULAR = 1.0   # rad/s


def keyeq(e, c):
    return e.char == c or e.keysym == c


def keydown(e):
    with state_lock:
        if keyeq(e, QUIT):
            shutdown()
            return
        if keyeq(e, UP):
            state[0] = True;  state[2] = False
        elif keyeq(e, DOWN):
            state[2] = True;  state[0] = False
        elif keyeq(e, LEFT):
            state[1] = True;  state[3] = False
        elif keyeq(e, RIGHT):
            state[3] = True;  state[1] = False


def keyup(e):
    with state_lock:
        if keyeq(e, UP):      state[0] = False
        elif keyeq(e, DOWN):  state[2] = False
        elif keyeq(e, LEFT):  state[1] = False
        elif keyeq(e, RIGHT): state[3] = False


def publish_cb(_):
    with state_lock:
        twist = Twist()
        if state[0]:   twist.linear.x =  MAX_LINEAR
        elif state[2]: twist.linear.x = -MAX_LINEAR
        if state[1]:   twist.angular.z =  MAX_ANGULAR
        elif state[3]: twist.angular.z = -MAX_ANGULAR
        if cmd_pub is not None:
            cmd_pub.publish(twist)


def shutdown():
    root.destroy()
    rospy.signal_shutdown("keyboard_teleop quit")


def main():
    global cmd_pub, root, MAX_LINEAR, MAX_ANGULAR

    MAX_LINEAR  = rospy.get_param("~speed", MAX_LINEAR)
    MAX_ANGULAR = rospy.get_param("~max_angular", MAX_ANGULAR)

    cmd_pub = rospy.Publisher("/cmd_vel", Twist, queue_size=1)
    rospy.Timer(rospy.Duration(0.1), publish_cb)

    root  = Tk()
    frame = Frame(root, width=100, height=100)
    frame.bind("<KeyPress>",   keydown)
    frame.bind("<KeyRelease>", keyup)
    frame.pack()
    frame.focus_set()
    Label(frame, height=10, width=32,
          text="Turtlebot2 Keyboard Teleop\n\n"
               "W  — forward\n"
               "S  — backward\n"
               "A  — turn left\n"
               "D  — turn right\n\n"
               "Q  — quit").pack()
    root.mainloop()


if __name__ == "__main__":
    rospy.init_node("turtlebot2_keyboard_teleop", disable_signals=True)
    signal.signal(signal.SIGINT, lambda s, f: shutdown())
    main()
