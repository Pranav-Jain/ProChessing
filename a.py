# -*- coding: utf-8 -*-
"""Untitled3.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1o_lnIExNiBScO2-bX9lCETGY3RCMnCg6
"""

import cv2
import numpy as np
import math
from skimage.filters import unsharp_mask
from PIL import Image, ImageDraw
from itertools import cycle
# from google.colab.patches import cv2_imshow

def draw_chessboard(pixel_width, n = 8):
  """
  Draw an n x n chessboard using PIL.
  """
  def sq_start(i):
      """
      Return the square corners, suitable for use in PIL drawings
      """
      return i*pixel_width / n

  def square(i, j):
      """
      Return the square corners, suitable for use in PIL drawing
      """
      return map(sq_start, [i, j, i+1, j+1])

  image = Image.new("L", (pixel_width, pixel_width))
  draw_square = ImageDraw.Draw(image).rectangle
  squares = (square(i,j)
             for i_start, j in zip(cycle((0, 1)), range(n))
             for i in range(i_start, n, 2))

  for sq in squares:
    # print(list(sq)[2:])
    ImageDraw.Draw(image).rectangle(tuple(sq), fill='white')
    image.save("chessboard.png")

def order_points(pts):
  # initialzie a list of coordinates that will be ordered
  # such that the first entry in the list is the top-left,
  # the second entry is the top-right, the third is the
  # bottom-right, and the fourth is the bottom-left
  rect = np.zeros((4, 2), dtype = "float32")
 
  # the top-left point will have the smallest sum, whereas
  # the bottom-right point will have the largest sum
  s = pts.sum(axis = 1)
  rect[0] = pts[np.argmin(s)]
  rect[2] = pts[np.argmax(s)]
 
  # now, compute the difference between the points, the
  # top-right point will have the smallest difference,
  # whereas the bottom-left will have the largest difference
  diff = np.diff(pts, axis = 1)
  rect[1] = pts[np.argmin(diff)]
  rect[3] = pts[np.argmax(diff)]
 
  # return the ordered coordinates
  return rect


def four_point_transform(image, pts):
  # obtain a consistent order of the points and unpack them
  # individually
  rect = order_points(pts)
  (tl, tr, br, bl) = rect
 
  # compute the width of the new image, which will be the
  # maximum distance between bottom-right and bottom-left
  # x-coordiates or the top-right and top-left x-coordinates
  widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
  widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
  maxWidth = max(int(widthA), int(widthB))
 
  # compute the height of the new image, which will be the
  # maximum distance between the top-right and bottom-right
  # y-coordinates or the top-left and bottom-left y-coordinates
  heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
  heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
  maxHeight = max(int(heightA), int(heightB))
 
  # now that we have the dimensions of the new image, construct
  # the set of destination points to obtain a "birds eye view",
  # (i.e. top-down view) of the image, again specifying points
  # in the top-left, top-right, bottom-right, and bottom-left
  # order
  dst = np.array([
    [0, 0],
    [maxWidth - 1, 0],
    [maxWidth - 1, maxHeight - 1],
    [0, maxHeight - 1]], dtype = "float32")
 
  # compute the perspective transform matrix and then apply it
  M = cv2.getPerspectiveTransform(rect, dst)
  warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
 
  # return the warped image
  return warped, min(maxHeight, maxWidth)

def get_edges(img):
  print(img.shape)

  meadian = np.mean(img)
  # print(np.mean(img))
  # print(np.median(img))
  # print(np.std(img))
  std = np.std(img)
  th1 = min(0,meadian - std)
  th2 = max(255,meadian + std)
  th1 = 100
  th2 = 200

  # th2, thresh_im = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
  # th1 = th2//3
  edges = cv2.Canny(img,th1,th2)
  # cv2.imwrite("drive/My Drive/Visual Chess Recognition/Edges.jpg",edges)
  cv2.imwrite("edges.jpg", edges)

  # warp = cv2.imread("warped.jpg")
  cdst = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
  lines = cv2.HoughLines(edges, 1, (np.pi/180), 100, None, 0, 0)

  return lines, cdst

def get_lines(lines, cdst):
  countV = 0
  countH = 0

  h_lines = []
  v_lines = []

  for i in range(len(lines)):
    # print(i)

    rho = lines[i][0][0]
    theta = lines[i][0][1]
    theta = theta*180/np.pi
    margin =10
    if(theta < 45 -margin or theta > 180 - 45 + margin):
      if(countV > 20):
        continue

      if (abs(rho)>3 and abs(rho < img.shape[1] - 3)):
        if rho < 0:
          v_lines.append([abs(rho), theta, -1])
        else:
          v_lines.append([rho, theta, 1])
        # v_lines.append([rho, theta])
        countV+=1
        # print(rho)
        # print("vertical")
        # print(theta*180/np.pi)
        a = math.cos(theta*np.pi/180)
        b = math.sin(theta*np.pi/180)
        x0 = a * rho
        y0 = b * rho
        pt1 = (int(x0 + 1000*(-b)), int(y0 + 1000*(a)))
        pt2 = (int(x0 - 1000*(-b)), int(y0 - 1000*(a)))
        cv2.line(cdst, pt1, pt2, (0,0,255), 3, cv2.LINE_AA)
    
    elif(theta > 45 + margin and theta < 135 - margin):
      if(countH > 20):
        continue

      if (abs(rho)>3 and abs(rho < img.shape[0] - 3)):
        if rho < 0:
          h_lines.append([abs(rho), theta, -1])
        else:
          h_lines.append([rho, theta, 1])
        countH+=1
        # print("horizontal")
        # print(theta*180/np.pi)
        a = math.cos(theta*np.pi/180)
        b = math.sin(theta*np.pi/180)
        x0 = a * rho
        y0 = b * rho
        pt1 = (int(x0 + 1000*(-b)), int(y0 + 1000*(a)))
        pt2 = (int(x0 - 1000*(-b)), int(y0 - 1000*(a)))
        cv2.line(cdst, pt1, pt2, (0,255,0), 3, cv2.LINE_AA)

  cv2.imwrite("lines.jpg",cdst)
  return h_lines, v_lines

def make_lines(h_lines, v_lines, cdst):
  
  print(h_lines.shape, v_lines.shape)
  for i in range(len(v_lines)):
    # print(i)

    rho = v_lines[i][0]*v_lines[i][2]
    theta = v_lines[i][1]
    # theta = theta*180/np.pi
    # margin =10
    # if(theta < 45 -margin or theta > 180 - 45 + margin):
    #   if(countV > 100):
    #     continue

    #   v_lines.append([rho, theta])
      # print(rho)
      # print("vertical")
      # print(theta*180/np.pi)
    # countV+=1
    a = math.cos(theta*np.pi/180)
    b = math.sin(theta*np.pi/180)
    x0 = a * rho
    y0 = b * rho
    pt1 = (int(x0 + 1000*(-b)), int(y0 + 1000*(a)))
    pt2 = (int(x0 - 1000*(-b)), int(y0 - 1000*(a)))
    cv2.line(cdst, pt1, pt2, (0,0,255), 3, cv2.LINE_AA)

  for i in range(len(h_lines)):
    rho = h_lines[i][0]*h_lines[i][2]
    theta = h_lines[i][1]
    a = math.cos(theta*np.pi/180)
    b = math.sin(theta*np.pi/180)
    x0 = a * rho
    y0 = b * rho
    pt1 = (int(x0 + 1000*(-b)), int(y0 + 1000*(a)))
    pt2 = (int(x0 - 1000*(-b)), int(y0 - 1000*(a)))
    cv2.line(cdst, pt1, pt2, (0,255,0), 3, cv2.LINE_AA)

  cv2.imwrite("final_lines.jpg",cdst)

# def unsharp_mask(image, kernel_size=(5, 5), sigma=1.0):
#   blurred = cv2.GaussianBlur(image, kernel_size, sigma)
#   sharpened = 2.0 * image - 1.0 * blurred
#   return sharpened.astype(np.uint8)


if __name__ == '__main__':

  image_name = "chess_1.jfif"
  img = cv2.imread(image_name)
  # img = unsharp_mask(img, radius=5, amount)

  lines, cd1 = get_edges(img)
  h_lines, v_lines = get_lines(lines, cd1)


  # cv2.imwrite("drive/My Drive/Visual Chess Recognition/Lines.jpg",cdst)

  h_lines = np.array(h_lines)
  v_lines = np.array(v_lines)
  h_lines = h_lines[h_lines[:,0].argsort()]
  v_lines = v_lines[v_lines[:,0].argsort()]

  # print(h_lines)
  # print(v_lines)

  pts = []
  voting = []
  for i in range(v_lines.shape[0]):
    intersections = []
    v = []
    for j in range(h_lines.shape[0]):
      A = np.zeros((2,2))
      b = np.zeros(2)
      A[0][0] = np.cos(v_lines[i][1] * np.pi/180)
      A[0][1] = np.sin(v_lines[i][1] * np.pi/180)
      A[1][0] = np.cos(h_lines[j][1] * np.pi/180)
      A[1][1] = np.sin(h_lines[j][1] * np.pi/180)

      b[0] = v_lines[i][2] * v_lines[i][0]
      b[1] = h_lines[j][2] * h_lines[j][0]

      x = np.linalg.solve(A, b)

      if(i == 0 and j == 0):
        pts.append(x)

      if(i == 0 and j == h_lines.shape[0] - 1):
        pts.append(x)
        # pts.append((abs(x[0]), abs(x[1])))

      if(i == v_lines.shape[0] - 1 and j == h_lines.shape[0] - 1):
        pts.append(x)
        # pts.append((abs(x[0]), abs(x[1])))

      if(i == v_lines.shape[0] - 1 and j == 0):
        pts.append(x)
        # pts.append((abs(x[0]), abs(x[1])))

  # pts[0], pts[2] = pts[2], pts[0]
  # pts[3], pts[1] = pts[1], pts[3]

  pts = np.array(pts)
  # print(pts)

  image = cv2.imread(image_name)

  warped, checkerboard_size = four_point_transform(image, pts)
  warped = cv2.resize(warped, (checkerboard_size, checkerboard_size))
  cv2.imwrite("warped.jpg", warped)
  warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)

  # warped = unsharp_mask(warped)

  # img = cv2.imread("warped.jpg", 0)
  # gaussian = cv2.GaussianBlur(warped, (3,3), 1.0)
  # warped = cv2.addWeighted(warped, 2, gaussian, -1, 0, warped)
  lines, cd2 = get_edges(warped)
  h_lines, v_lines = get_lines(lines, np.copy(cd2))

  h_lines = np.array(h_lines)
  v_lines = np.array(v_lines)
  h_lines = h_lines[h_lines[:,0].argsort()]
  v_lines = v_lines[v_lines[:,0].argsort()]

  X = []

  for i in range(v_lines.shape[0]):
    x_temp = []
    for j in range(h_lines.shape[0]):
      A = np.zeros((2,2))
      b = np.zeros(2)
      A[0][0] = np.cos(v_lines[i][1] * np.pi/180)
      A[0][1] = np.sin(v_lines[i][1] * np.pi/180)
      A[1][0] = np.cos(h_lines[j][1] * np.pi/180)
      A[1][1] = np.sin(h_lines[j][1] * np.pi/180)

      b[0] = v_lines[i][2] * v_lines[i][0]
      b[1] = h_lines[j][2] * h_lines[j][0]

      x = np.linalg.solve(A, b)
      x_temp.append(x)

    X.append(x_temp)

  X = np.array(X)
  square = []
  for i in range(X.shape[0] - 1):
    for j in range(X.shape[1] - 1):
      a = np.linalg.norm(X[i][j] - X[i][j+1])
      b = np.linalg.norm(X[i+1][j] - X[i+1][j+1])
      c = np.linalg.norm(X[i][j] - X[i+1][j])
      d = np.linalg.norm(X[i][j+1] - X[i+1][j+1])
      if abs(a - b) < 2 and abs(c - d) < 2 and abs(a -c) < 2 and abs(b -d) < 2 and a>10:
        # print(a,b,c,d)
        square = [i, j, v_lines[i], h_lines[j], a]
        break

  # print(square)
  h_lines_final = []
  v_lines_final = []

  h_lines_final.append(square[3])
  # h_lines_final.append(h_lines[square[1]+1])
  v_lines_final.append(square[2])
  # v_lines_final.append(v_lines[square[0]+1])

  threshold = square[-1]*0.25
  counter = 0
  for j in range(X.shape[0] - square[0] - 1):
    counter += 1
    m = np.inf
    index = -1
    for i in range(square[0] + 1, X.shape[0]):
      # for j in range(v_lines.shape[0]):
      # print(i, abs(np.linalg.norm(X[square[0]][square[1]] - X[j][square[1]]) - counter*square[-1]))
      x = abs(abs(v_lines[i][0] - v_lines[square[0]][0]) - counter*square[-1])
      if x < m:
        m = x
        index = i
    if m < threshold:  
      v_lines_final.append(v_lines[index])

  counter = 0
  for j in range(square[0]):
    counter += 1
    m = np.inf
    index = -1
    for i in range(square[0] -1, -1, -1):
      # for j in range(v_lines.shape[0]):
      # print(j, abs(np.linalg.norm(X[square[0]][square[1]] - X[i][square[1]]) - counter*square[-1]))
      x = abs(abs(v_lines[i][0] - v_lines[square[0]][0]) - counter*square[-1])
      # print(x)
      if x < m:
        m = x
        index = i
    if m < threshold:
      v_lines_final.append(v_lines[index])
        

  counter = 0
  for j in range(X.shape[1] - square[1] - 1):
    counter += 1
    m = np.inf
    index = -1
    for i in range(square[1] + 1, X.shape[1]):
      # print(i, abs(np.linalg.norm(X[square[0]][square[1]] - X[square[0]][j]) - counter*square[-1]))
      x = abs(abs(h_lines[i][0] - h_lines[square[1]][0]) - counter*square[-1])
      if x < m:
        m = x
        index = i
    if m < threshold:
      h_lines_final.append(h_lines[index])

  counter = 0
  for j in range(square[1]):
    counter += 1
    m = np.inf
    index = -1
    for i in range(square[1]-1, -1, -1):
      x = abs(abs(h_lines[i][0] - h_lines[square[1]][0]) - counter*square[-1])
      if x < m:
        m = x
        index = i
    if m < threshold:
      h_lines_final.append(h_lines[index])

  h_lines_final = np.array(h_lines_final)
  v_lines_final = np.array(v_lines_final)

  # edges = cv2.imread("edges.jpg", 0)
  h_lines = h_lines_final[h_lines_final[:,0].argsort()]
  v_lines = v_lines_final[v_lines_final[:,0].argsort()]

  if h_lines.shape[0] > 9:
    h_lines = h_lines[:9]

  print(v_lines)
  print(h_lines)

  make_lines(h_lines_final, v_lines_final, cd2)

  pts = []
  voting = []
  for i in range(v_lines.shape[0]):
    intersections = []
    v = []
    for j in range(h_lines.shape[0]):
      A = np.zeros((2,2))
      b = np.zeros(2)
      A[0][0] = np.cos(v_lines[i][1] * np.pi/180)
      A[0][1] = np.sin(v_lines[i][1] * np.pi/180)
      A[1][0] = np.cos(h_lines[j][1] * np.pi/180)
      A[1][1] = np.sin(h_lines[j][1] * np.pi/180)

      b[0] = v_lines[i][2] * v_lines[i][0]
      b[1] = h_lines[j][2] * h_lines[j][0]

      x = np.linalg.solve(A, b)

      if(i == 0 and j == 0):
        pts.append(x)

      if(i == 0 and j == h_lines.shape[0] - 1):
        pts.append(x)
        # pts.append((abs(x[0]), abs(x[1])))

      if(i == v_lines.shape[0] - 1 and j == h_lines.shape[0] - 1):
        pts.append(x)
        # pts.append((abs(x[0]), abs(x[1])))

      if(i == v_lines.shape[0] - 1 and j == 0):
        pts.append(x)
        # pts.append((abs(x[0]), abs(x[1])))

  # pts[0], pts[2] = pts[2], pts[0]
  # pts[3], pts[1] = pts[1], pts[3]

  pts = np.array(pts)
  # print(pts)

  image = cv2.imread("warped.jpg")

  warped, checkerboard_size = four_point_transform(image, pts)
  warped = cv2.resize(warped, (checkerboard_size, checkerboard_size))
  cv2.imwrite("warped.jpg", warped)
  warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)


  X = []

  for i in range(v_lines.shape[0]):
    x_temp = []
    for j in range(h_lines.shape[0]):
      A = np.zeros((2,2))
      b = np.zeros(2)
      A[0][0] = np.cos(v_lines[i][1] * np.pi/180)
      A[0][1] = np.sin(v_lines[i][1] * np.pi/180)
      A[1][0] = np.cos(h_lines[j][1] * np.pi/180)
      A[1][1] = np.sin(h_lines[j][1] * np.pi/180)

      b[0] = v_lines[i][2] * v_lines[i][0]
      b[1] = h_lines[j][2] * h_lines[j][0]

      x = np.linalg.solve(A, b)
      x_temp.append(x)

    X.append(x_temp)

  X = np.array(X)
  print(X)

  # #     # print(x)
  #     if int(x[0]) not in intersections:
  #       # for k in np.arange(np.floor(x[0])-5, np.floor(x[0])+5, 1):
  #         # intersections.append(k)
  #       intersections.append(np.ceil(x[0]))
  #       intersections.append(np.floor(x[0]))
  #       v.append(True)
  #     else:
  #       v.append(False)

  #     # print(intersections)
  #   voting.append(v)
  #   # exit()

  # # print(voting)
  # voting = np.array(voting)

  # final_vote = np.all(voting, axis=0)
  # # print(len(final_vote))

  # v_lines_final = []
  # for i in range(len(final_vote)):
  #   if final_vote[i] ==True:
  #     # if v_lines[i][0] >= 2 and v_lines[i][0] <= img.shape[0] - 2:
  #     v_lines_final.append(v_lines[i])

  # print(len(v_lines_final))




  # voting = []
  # for i in range(v_lines.shape[0]):
  #   intersections = []
  #   h = []
  #   for j in range(h_lines.shape[0]):
  #     A = np.zeros((2,2))
  #     b = np.zeros(2)
  #     A[0][0] = np.cos(v_lines[i][1] * np.pi/180)
  #     A[0][1] = np.sin(v_lines[i][1] * np.pi/180)
  #     A[1][0] = np.cos(h_lines[j][1] * np.pi/180)
  #     A[1][1] = np.sin(h_lines[j][1] * np.pi/180)

  #     b[0] = v_lines[i][0]
  #     b[1] = h_lines[j][0]

  #     x = np.linalg.solve(A, b)
  #     # print(x)
  #     if int(x[1]) not in intersections:
  #       intersections.append(np.ceil(x[1]))
  #       intersections.append(np.floor(x[1]))
  #       h.append(True)
  #     else:
  #       h.append(False)

  #     # print(intersections)
  #   voting.append(h)
  #   # exit()

  # # print(voting)
  # voting = np.array(voting)

  # final_vote = np.all(voting, axis=0)
  # # print(len(final_vote))

  # h_lines_final = []
  # for i in range(len(final_vote)):
  #   if final_vote[i] ==True:
  #     h_lines_final.append(h_lines[i])

  # print(len(h_lines_final))


  # cdst = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
  # for i in range(len(v_lines_final)):
  #   # print(i)

  #   rho = v_lines_final[i][0]
  #   theta = v_lines_final[i][1]
  #   # theta = theta*180/np.pi
  #   # margin =10
  #   # if(theta < 45 -margin or theta > 180 - 45 + margin):
  #   #   if(countV > 100):
  #   #     continue

  #   #   v_lines.append([rho, theta])
  #     # print(rho)
  #     # print("vertical")
  #     # print(theta*180/np.pi)
  #   countV+=1
  #   a = math.cos(theta*np.pi/180)
  #   b = math.sin(theta*np.pi/180)
  #   x0 = a * rho
  #   y0 = b * rho
  #   pt1 = (int(x0 + 1000*(-b)), int(y0 + 1000*(a)))
  #   pt2 = (int(x0 - 1000*(-b)), int(y0 - 1000*(a)))
  #   cv2.line(cdst, pt1, pt2, (0,0,255), 2, cv2.LINE_AA)

  # for i in range(len(h_lines_final)):
  #   rho = h_lines_final[i][0]
  #   theta = h_lines_final[i][1]
  #   countH+=1
  #   a = math.cos(theta*np.pi/180)
  #   b = math.sin(theta*np.pi/180)
  #   x0 = a * rho
  #   y0 = b * rho
  #   pt1 = (int(x0 + 1000*(-b)), int(y0 + 1000*(a)))
  #   pt2 = (int(x0 - 1000*(-b)), int(y0 - 1000*(a)))
  #   cv2.line(cdst, pt1, pt2, (0,255,0), 2, cv2.LINE_AA)

  # cv2.imwrite("final_lines.jpg",cdst)


  # print(h_lines_final)
  # print("\n")
  # print(v_lines_final)




######################################################################################

# cdstP = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
# linesP = cv2.HoughLinesP(edges, 1, (np.pi / 180), 50, None, 50, 10)

# if linesP is not None:
#     for i in range(0, len(linesP)):
#         l = linesP[i][0]
#         cv2.line(cdstP, (l[0], l[1]), (l[2], l[3]), (0,0,255), 3, cv2.LINE_AA)
# # cv2.imwrite("drive/My Drive/Visual Chess Recognition/Lines.jpg",cdstP)
# cv2_imshow(cdstP)


######################################## References ###############################################
# https://www.pyimagesearch.com/2014/08/25/4-point-opencv-getperspective-transform-example/
