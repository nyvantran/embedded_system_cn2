import cv2

img = cv2.imread('1.png')
img1 = cv2.rotate(img, 2)
cv2.imshow('test', img)
cv2.imshow('test1', img1)
cv2.waitKey(0)
cv2.destroyAllWindows()
