#!/usr/bin/python3
#-*- coding: utf-8 -*-

import rospy
import roslib
from sensor_msgs.msg import Image
from sensor_msgs.msg import CameraInfo 
from l3xz_openmv_camera.srv import rgb, rgbResponse

import threading
import cv2
import numpy as np
from camera_interface import OpenMvInterface

import time

omv_cam = None
mutex = threading.Lock()
def rgb_callback(request):
  global omv_cam
  global mutex
  mutex.acquire()
  success = omv_cam.rgb_led(request.r, request.g, request.b)
  mutex.release()
  print(success)
  return rgbResponse(success)

def main():
  global omv_cam
  rospy.init_node('openmv')

  frame_id = rospy.get_param("~frame_id", "odom")

  show = rospy.get_param("~show_image", False)

  rate = rospy.Rate(rospy.get_param("~rate_hz", 10))

  omv_cam = OpenMvInterface(rospy.get_param("~port", "/dev/ttyACM0"),
     rospy.get_param("~camera_script", "/home/pi/catkin_ws/src/l3xz_openmv_camera/scripts/camera_script.py"))

  service = rospy.Service('rgb', rgb, rgb_callback)

  img_name = rospy.get_param("~image_topic", "image_color")
  pub_image = rospy.Publisher(img_name,
          Image, queue_size = rospy.get_param("~image_queue", 1))
  pub_info = rospy.Publisher(rospy.get_param("~info_topic", "camera_info"),
          CameraInfo, queue_size = rospy.get_param("~image_queue", 1))

  img_msg = Image()
  img_msg.header.frame_id = frame_id

  info_msg = CameraInfo()
  info_msg.header.frame_id = frame_id

  global mutex
  while not rospy.is_shutdown():
    mutex.acquire()
    framedump = omv_cam.dump()
    mutex.release()
    if framedump is not None:
      if show:
        cv2.imshow(img_name, framedump.pixels)
        cv2.waitKey(1)
      time = rospy.Time.now()
      img_msg.header.stamp = time 
      pub_image.publish(framedump.fill_img_msg(img_msg))

      info_msg.header.stamp = time
      pub_info.publish(framedump.fill_info_msg(info_msg))
      
    rate.sleep()

if __name__ == '__main__':
  main()
