# -*- coding: utf-8 -*-
"""Untitled3.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1o_lnIExNiBScO2-bX9lCETGY3RCMnCg6
"""

import cv2
import numpy as np
import math
# from google.colab.patches import cv2_imshow

img = cv2.imread("chess_1.jfif")
print(img.shape)

meadian = np.mean(img)
print(np.mean(img))
print(np.median(img))
print(np.std(img))
std = np.std(img)
th1 = min(0,meadian - std)
th2 = max(255,meadian + std)
th1 = 150
th2 = 450
edges = cv2.Canny(img,th1,th2)
# cv2.imwrite("drive/My Drive/Visual Chess Recognition/Edges.jpg",edges)
cv2.imwrite("edges.jpg", edges)

cdst = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
lines = cv2.HoughLines(edges, 1, (np.pi/180), 100, None, 0, 0)
countV = 0
countH = 0

if lines is not None:
  print(lines)

lines = np.array(lines)



for i in range(len(lines)):
  # print(i)

  rho = lines[i][0][0]
  theta = lines[i][0][1]
  theta = theta*180/np.pi
  margin =10
  if(theta < 45 -margin or theta > 180 - 45 + margin):
    # print(rho)
    # print("vertical")
    # print(theta*180/np.pi)
    if(countV >= 19):
      continue
    countV+=1
    a = math.cos(theta*np.pi/180)
    b = math.sin(theta*np.pi/180)
    x0 = a * rho
    y0 = b * rho
    pt1 = (int(x0 + 1000*(-b)), int(y0 + 1000*(a)))
    pt2 = (int(x0 - 1000*(-b)), int(y0 - 1000*(a)))
    cv2.line(cdst, pt1, pt2, (0,0,255), 3, cv2.LINE_AA)
  elif(theta > 45 + margin and theta < 135 - margin):
    # print("horizontal")
    # print(theta*180/np.pi)
    if(countH >= 19):
      continue
    countH+=1
    a = math.cos(theta*np.pi/180)
    b = math.sin(theta*np.pi/180)
    x0 = a * rho
    y0 = b * rho
    pt1 = (int(x0 + 1000*(-b)), int(y0 + 1000*(a)))
    pt2 = (int(x0 - 1000*(-b)), int(y0 - 1000*(a)))
    cv2.line(cdst, pt1, pt2, (0,255,0), 3, cv2.LINE_AA)

# cv2.imwrite("drive/My Drive/Visual Chess Recognition/Lines.jpg",cdst)
cv2.imwrite("lines.jpg",cdst)

# cdstP = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
# linesP = cv2.HoughLinesP(edges, 1, (np.pi / 180), 50, None, 50, 10)

# if linesP is not None:
#     for i in range(0, len(linesP)):
#         l = linesP[i][0]
#         cv2.line(cdstP, (l[0], l[1]), (l[2], l[3]), (0,0,255), 3, cv2.LINE_AA)
# # cv2.imwrite("drive/My Drive/Visual Chess Recognition/Lines.jpg",cdstP)
# cv2_imshow(cdstP)


