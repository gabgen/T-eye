#!/usr/bin/env python
# coding: utf-8

from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2
import numpy as np
from matplotlib import pyplot as plt
import statistics
import os



#====[PARAMETERS DEFINITION]====
KERNEL_SIZE=11
MINIMUM_SIDE_SIZE=3 #in pixels
CANNY_LOWERBOUND=70 #Canny bounds are used to detect edges(hysteresis)
CANNY_UPPERBOUND=100 #Canny bounds are used to detect edges(hysteresis)
EXTERNAL_SCALE=1.2
INTERNAL_SCALE=0.5
DELTA_LOCKED=25

#====[CAMERA REFERENCE]====
camera = PiCamera()
c_list=[]

#Display the image taken from the PiCamera
def display_image(im_data):
    dpi=80
    height, width, depth = im_data.shape
    figsize = width / float(dpi), height / float(dpi)
    fig = plt.figure(figsize=figsize)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis('off')
    ax.imshow(im_data, cmap='gray')
    plt.show()
    plt.pause(0.001)
    
#Resize the image from the PiCamera and crop it. The object should be at the center of the image. The output is the modified image
def resize_and_crop_image(img,resize_scale,crop_scaleW,crop_scaleH):
    width = int(img.shape[1] * resize_scale)
    height = int(img.shape[0] * resize_scale) 
    img = cv2.resize(img, (width,height), interpolation = cv2.INTER_AREA) 
    changerW=(width/2)*crop_scaleW
    changerH=(height/2)*crop_scaleH
    img = img[int(height/2-changerH):int(height/2+changerH),int(width/2-changerW):int(width/2+changerW)]
    return img


#The output is the median of the r,g,b channel of the contour points
def get_rgb_median(cnt,img):
    rgb_r=[]
    rgb_g=[]
    rgb_b=[]
    for i in range(len(cnt)):
        x=cnt[i][0][0]
        y=cnt[i][0][1]
        try:
            rgb_r.append(img[y][x][0])
            rgb_g.append(img[y][x][1])
            rgb_b.append(img[y][x][2])
        except:
            pass
    return statistics.median(rgb_r),statistics.median(rgb_g),statistics.median(rgb_b)
    
#Check if cX,Cy and 8 close points are inside the contour
def polygonTest(array,c,cX,cY):
    array.append(cv2.pointPolygonTest(c,(cX,cY),True))
    array.append(cv2.pointPolygonTest(c,(cX+MINIMUM_SIDE_SIZE,cY),True))
    array.append(cv2.pointPolygonTest(c,(cX,cY+MINIMUM_SIDE_SIZE),True))
    array.append(cv2.pointPolygonTest(c,(cX-MINIMUM_SIDE_SIZE,cY),True))
    array.append(cv2.pointPolygonTest(c,(cX,cY-MINIMUM_SIDE_SIZE),True))
    array.append(cv2.pointPolygonTest(c,(cX+MINIMUM_SIDE_SIZE,cY+MINIMUM_SIDE_SIZE),True))
    array.append(cv2.pointPolygonTest(c,(cX+MINIMUM_SIDE_SIZE,cY-MINIMUM_SIDE_SIZE),True))
    array.append(cv2.pointPolygonTest(c,(cX-MINIMUM_SIDE_SIZE,cY+MINIMUM_SIDE_SIZE),True))
    array.append(cv2.pointPolygonTest(c,(cX-MINIMUM_SIDE_SIZE,cY-MINIMUM_SIDE_SIZE),True))

def scale_contour(cnt, scale, cx, cy):
    cnt_norm = cnt - [cx, cy]
    cnt_scaled = cnt_norm * scale
    cnt_scaled = cnt_scaled + [cx, cy]
    cnt_scaled = cnt_scaled.astype(np.int32)
    return cnt_scaled


def get_preprocess_image(img):
    #img = cv2.imread(path)
    #cv2.imshow("Loaded image RGB", img)
    edges = cv2.Canny(img,CANNY_LOWERBOUND,CANNY_UPPERBOUND)
    #cv2.imshow("Canny edges detection", edges)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(KERNEL_SIZE,KERNEL_SIZE))
    closing = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
    #cv2.imshow("Closing capture", closing)

    cntsimg=img.copy()
    _, cnts, _ = cv2.findContours(closing.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    num_pieces_locked=0
    num_pieces_unlocked=0
    for c in cnts:
        # compute the center of the contour
        M = cv2.moments(c)
        if(M["m00"]!=0): 
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            check=[]
            polygonTest(check,c,cX,cY)                
            if any(check_element < 0 for check_element in check):
                cv2.circle(cntsimg, (cX, cY), 2, (0, 255, 255), -1)
                cv2.drawContours(cntsimg, [c], -1, (0, 0, 255), 1)
            else:                
                c_external=scale_contour(c, EXTERNAL_SCALE, cX, cY)
                c_internal=scale_contour(c, INTERNAL_SCALE, cX, cY)
                cv2.circle(cntsimg, (cX, cY), 2, (255, 255, 0), -1)
                c_list.append([cX,cY])
                cv2.drawContours(cntsimg, [c], -1, (0, 255, 0), 1)
                cv2.drawContours(cntsimg, [c_external], -1, (255, 0, 0), 1)
                cv2.drawContours(cntsimg, [c_internal], -1, (255, 0, 0), 1)
                r_median_ex,g_median_ex,b_median_ex = get_rgb_median(c_external,img)
                r_median_in,g_median_in,b_median_in = get_rgb_median(c_internal,img)
                #print('external: '+str(r_median_ex)+'|'+str(g_median_ex)+'|'+str(b_median_ex))
                #print('internal: '+str(r_median_in)+'|'+str(g_median_in)+'|'+str(b_median_in))
                if(abs(int(r_median_ex)-int(r_median_in))<DELTA_LOCKED):
                    num_pieces_locked=num_pieces_locked+1
                    cv2.drawContours(cntsimg, [c], -1, (0, 0, 255), 1)
                else: num_pieces_unlocked=num_pieces_unlocked+1
    #Save the center coordinates of the cut elements in a txt file
    center_list = open("c_list.txt","w") 
    for x in c_list:
    center_list.write(str(x)+'\n')
    center_list.close()           

    cv2.circle(cntsimg, (100, 500), 5, (100, 255, 100), -1)    
    cv2.imshow("Results",cntsimg)
    return cntsimg,num_pieces_locked,num_pieces_unlocked
    


while(1):

    rawCapture = PiRGBArray(camera)
    camera.capture(rawCapture, format="rgb")
    image = rawCapture.array
    image = resize_and_crop_image(image,0.5,0.5,1)
    image,num_pieces_locked,num_pieces_unlocked = get_preprocess_image(image)




cv2.waitKey(0) # waits until a key is pressed
cv2.destroyAllWindows() # destroys the window showing image

