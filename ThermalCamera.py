#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import numpy as np
import math 
import matplotlib.pyplot as plt


#==========[Parameters]============
OUTPUT_W=24*2
OUTPUT_H=32*2
HEIGHT=500
WIDTH=500


#==========[Test center list]============
center_list=[[5,7],[75,86],[300,460]]


#==========[Functions]============

def get_matrix():
    matrix=[]
    thermal_matrix = open('tmatrix.txt').read()
    thermal_matrix = [item.split() for item in matrix.split(' ')[:-1]]
    for item in thermal_matrix:
        matrix.append(float(item[0]))
    thermal_matrix.close()
    return matrix
        

def preprocess_matrix(matrix):
    matrix=np.asarray(matrix, dtype=np.float32)    
    matrix=np.reshape(matrix, (OUTPUT_W, OUTPUT_H))
    matrix=matrix.transpose()
    matrix=np.flip(matrix, 1)
    return matrix

    
def check_matrix(c_list,matrix):
    
    for pt in c_list:
        
        cX=pt[0]
        cY=pt[1]
        new_cX=math.trunc(cX*OUTPUT_W/width)
        new_cY=math.trunc(cY*OUTPUT_H/HEIGHT)

        for x in range(new_cX-3,new_cX+3):
            if x>=0 and x<OUTPUT_W :
                for y in range(new_cY-3,new_cY+3):
                    if y>=0 and y<OUTPUT_H :
                        if matrix[x][y]>40:
                            print("Defect in {},{} \n".format(cX,cY))
                            defect_centers.append([cX,cY])
        return defect_centers
    

    
#==========[Main]============

while(1) :
    defect_centers=[]
    current_matrix= get_matrix()
    current_matrix= preprocess_matrix(current_matrix)
    defect_centers= check_matrix(center_list,current_matrix)
    

    

