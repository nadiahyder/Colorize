README 

methodolgy and output are presented on this site: https://inst.eecs.berkeley.edu/~cs194-26/fa20/upload/files/proj1/cs194-26-aeg/ 

to run the code: python main.py

Running main.py performs colorization on all images (.tif and .jpg) in the current directory and saves the colorized images as a jpg in the current directory, named 'colorized_' + original image name. It also outputs the name, displacements (green then red), and runtime of each image. 

main.py works by reading all files, beginning a timer, dividing the image into b,g,r, cropping the images, calculating layers of the image pyramid, and then using the image pyramid to align the channels (using ssd on the edges). The aligned images are then outputted and saved. 
