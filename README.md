# T-eye
Autonomous recognition of defect in laser cutting processed element

![GitHub Logo](https://github.com/gabriele1295/T-eye/blob/main/T-eye%20Images/image.png)
### What it is ? 
T-eye is a simple software aimed to recognise a stuck element in metal piece after a laser cutting process. 
## Hardware components & Software
### Hardware
 - RaspberryPi3-B+
 - Picamera
 - Thermal Camera ( https://shop.pimoroni.com/products/mlx90640-thermal-mera-breakout?variant=12536948654163 )
 - External Case 
### Software 
Python 3.6 with the following libraries :
- picamera 
- OpenCV
- numpy 
- matplotlib 
- statistics

Files: 
- rgb_analysis.py 
- thermal_analysis.py
- mlx90640.tar (for runnig the thermal camera)


## How does T-eye work ? 
T-eye relies on two simultaneous analysis: an image analysis and a thermal analysis. Indeed thorugh the RGB module of the Picamera T-eye is able to analyse the metal piece in front of it recognise which are the part of the piece that have been cut. Then It tries to measure the differences between the interior area of the cut element and the external one. If the two areas are too similar implies that a stuck element is found. Simultaneously a second branch of the software analises the thermal image in order to recognise points where the temperature is too high, related to a stuck element in the piece. 
For more info you can read "T-eye report".


The two files "rgb_analysis.py" and "thermal_analysis.py" are the two aformentioned branches of the software . The element that links those two branches are "c_list.txt" . Indeed "c_list.txt" contains a list of the centers that could be defected saved by the "rgb_analysis.py" . Then the "thermal_analysis.py" read the centers location and match it with the thermal matrix in order to check the defect.

