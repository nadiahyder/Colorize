#%%
import math
import numpy as np
import skimage as sk
import skimage.feature
import skimage.io as skio
import skimage.transform as sktr
import time


# crops the outer 15% of the image. maintains inner 85%
def crop_center(pil_img):
    img_width, img_height = pil_img.shape

    crop_width = (int)(8.5*img_width/10)
    remaining_width = (int)((img_width - crop_width)/2)

    crop_height = (int)(8.5*img_height/10)
    remaining_height = (int)((img_height - crop_height) / 2)

    im = pil_img[remaining_width: img_width-remaining_width, remaining_height: img_height - remaining_height]
    return im

# performs edge detection using canny filtering
def get_edges(A):
    return sk.feature.canny(A, 3)

def pyramid_align(r, g, b, num_runs, displacements):

    # base case
    if num_runs == 0:
        print(displacements)
        return np.dstack((r,g,b))

    factor = 2 ** num_runs

    # rescale the images
    new_r = get_edges(sktr.rescale(r, 1 / factor))
    new_g = get_edges(sktr.rescale(g, 1 / factor))
    new_b = get_edges(sktr.rescale(b, 1 / factor))

    ag_d = get_displacement(new_g, new_b)
    ag = align(new_g, ag_d)

    ar_d = get_displacement(new_r, ag)

    # align original images relative to rescaled image displacement
    g = align(g, [ag_d[0] * factor, ag_d[1] * factor])
    r = align(r, [ar_d[0] * factor, ar_d[1] * factor])

    # first row is green displacement
    # second row is red displacement
    # multiply to keep track of displacement
    displacements[0][0] += ag_d[0] * factor
    displacements[0][1] += ag_d[1] * factor
    displacements[1][0] += ar_d[0] * factor
    displacements[1][1] += ar_d[1] * factor

    return pyramid_align(r, g, b, num_runs-1, displacements)

# sum of square distances
def ssd(im1, im2):
    return np.sum(np.sum((im1^im2)**2))

def horizontal_shift(img, n):
    return np.roll(img, n, axis=1)

def vertical_shift(img, n):
    return np.roll(img, n, axis=0)

# returns best dx dy displacement
def get_displacement(A, B, threshold=15):
    dx = 0
    dy = 0
    min_ssd = ssd(A, B)

    for u in range(-1 * threshold, threshold):
        for v in range(-1 * threshold, threshold):
            displaced_img = align(A, [u,v])
            new_ssd = ssd(displaced_img, B)

            if new_ssd < min_ssd:
                dx = u
                dy = v
                min_ssd = new_ssd
    return [dx, dy]

# aligns images using horizontal and vertical shift
def align(A, d):
    return horizontal_shift(vertical_shift(A, d[1]), d[0])

# calls the appropriate functions for image processing
# cropping, image pyramid, output
def colorize(file):
    print(file)
    name = file.split('.')[0] + '.jpg'

    # run a timer
    start_time = time.time()
    imname = file
    im = skio.imread(imname)

    im = sk.img_as_float(im)

    # compute the height of each part (just 1/3 of total)
    height = np.floor(im.shape[0] / 3.0).astype(np.int)

    # separate color channels
    b = im[:height]
    g = im[height: 2 * height]
    r = im[2 * height: 3 * height]

    b = crop_center(b)
    g = crop_center(g)
    r = crop_center(r)

    # number of levels in image pyramid
    num_runs = math.floor(math.log2(b.shape[1] / 100))

    displacements = [[0, 0], [0, 0]]
    rgb = pyramid_align(r, g, b, num_runs, displacements)

    print("Runtime: %.5s seconds" % (time.time() - start_time))
    
    rgb = 255 * rgb # Now scale by 255
    img = rgb.astype(np.uint8)

    # save the image
    fname = 'colorized_' + name
    skio.imsave(fname, img)

    # display the image
    skio.imshow(img)
    skio.show()

# read in all images and colorize them
import os
files = [f for f in os.listdir('.') if os.path.isfile(f)]
for file in files:

    if not file.endswith(".tif") and not file.endswith(".jpg"):
        continue

    colorize(file)
