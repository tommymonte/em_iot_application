import numpy as np
from PIL import Image
# Transform RGB array to Lab array
from skimage.color import rgb2lab, lab2rgb
# Transform RGB to HSV
from skimage.color import rgb2hsv, hsv2rgb
# Histogram equalization on the V channel
from skimage.exposure import equalize_hist
from skimage import exposure
import os
import matplotlib.pyplot as plt
import statistics
import math
import sys
from dataclasses import dataclass
import time
from typing import Tuple

#model constant
Y = 0.7755
W0 = 1.48169521*pow(10,-6)
WR = 2.13636845*pow(10,-7)
WG = 1.77746705*pow(10,-7)
WB = 2.14348309*pow(10,-7)
P1 = 4.251e-5
P2 = -3.029e-4
P3 = 3.024e-5
DEBUG = 0
SUBSET = 0
IMAGE_PATHS = "./test_image"
IMAGE_PATHS_DEBUG = "./test_image/subset"

image_paths2 = "./test_image/subset"

files2 = [f for f in os.listdir(image_paths2) if f.endswith('.tiff') or f.endswith('.jpg')]

image_paths = "./test_image/train"

files = [f for f in os.listdir(image_paths) if f.endswith('.tiff') or f.endswith('.jpg')]

image_paths_tiff = "./test_image/tiff"

tiff = [f for f in os.listdir(image_paths_tiff) if f.endswith('.tiff') or f.endswith('.jpg')]

image_paths_screen = "./test_image/screen"

screen = [f for f in os.listdir(image_paths_screen) if f.endswith('.tiff') or f.endswith('.jpg')]

DATASET = files
DATASET_PATH = image_paths
@dataclass
class Tranformation_pareto:
    min_power_gain_index: int
    max_power_gain_index: int
    min_distortion_index: int
    max_distortion_index: int

@dataclass
class Distortion_list:
    def __init__(self, data=None):
        self.list = data if data is not None else []

    def distortion_list(self):
        if not isinstance(self.list, list):  
            raise TypeError(f"self.list non è una lista! È {type(self.list)}")
        return [item[0] for item in self.list]  

    def power_list(self):
        if not isinstance(self.list, list):  
            raise TypeError(f"self.list non è una lista! È {type(self.list)}")
        return [item[1] for item in self.list]  


def rgba2rgb( rgba, background=(255,255,255) ):
    row, col, ch = rgba.shape

    if ch == 3:
        return rgba

    assert ch == 4, 'RGBA image has 4 channels.'

    rgb = np.zeros( (row, col, 3), dtype='float32' )
    r, g, b, a = rgba[:,:,0], rgba[:,:,1], rgba[:,:,2], rgba[:,:,3]

    a = np.asarray( a, dtype='float32' ) / 255.0

    R, G, B = background

    rgb[:,:,0] = r * a + (1.0 - a) * R
    rgb[:,:,1] = g * a + (1.0 - a) * G
    rgb[:,:,2] = b * a + (1.0 - a) * B

    return np.asarray( rgb, dtype='uint8' )

def progressbar(it, prefix="", size=60, out=sys.stdout): # Python3.6+
    count = len(it)
    start = time.time() # time estimate start
    def show(j):
        x = int(size*j/count)
        # time estimate calculation and string
        remaining = ((time.time() - start) / j) * (count - j)        
        mins, sec = divmod(remaining, 60) # limited to minutes
        time_str = f"{int(mins):02}:{sec:03.1f}"
        print(f"{prefix}[{u'█'*x}{('.'*(size-x))}] {j}/{count} Est wait {time_str}", end='\r', file=out, flush=True)
    show(0.1) # avoid div/0 
    for i, item in enumerate(it):
        yield item
        show(i+1)
    print("\n", flush=True, file=out)

def image_color_contrib(image):
    r, g, b = image[:, :, 0], image[:, :, 1], image[:, :, 2]

    # Plot histograms
    plt.figure(figsize=(12, 5))
    plt.hist(r.ravel(), bins=256, color="red", alpha=0.5, label="Red")
    plt.hist(g.ravel(), bins=256, color="green", alpha=0.5, label="Green")
    plt.hist(b.ravel(), bins=256, color="blue", alpha=0.5, label="Blue")

    plt.xlabel("Pixel Intensity (0-255)")
    plt.ylabel("Frequency")
    plt.title("Color Channel Contribution")
    plt.legend()
    plt.show()

    r_mean = np.mean(image[:, :, 0])  # Mean intensity of Red channel
    g_mean = np.mean(image[:, :, 1])  # Mean intensity of Green channel
    b_mean = np.mean(image[:, :, 2])  # Mean intensity of Blue channel

    # Labels and values
    channels = ["Red", "Green", "Blue"]
    values = [r_mean, g_mean, b_mean]
    colors = ["red", "green", "blue"]

    # Plot the bar chart
    plt.figure(figsize=(6, 4))
    plt.bar(channels, values, color=colors, alpha=0.7)

    plt.xlabel("Color Channel")
    plt.ylabel("Average Intensity")
    plt.title("Average Contribution of RGB Channels")
    plt.ylim(0, 255)  # Pixel intensity range

    plt.show()
    return

def image_sv_contrib(image):
    h, s, v = image[:, :, 0], image[:, :, 1], image[:, :, 2]

    # Plot histograms
    plt.figure(figsize=(12, 5))
    plt.hist(s.ravel(), bins=50, color="green", alpha=0.5, label="S")
    plt.hist(v.ravel(), bins=50, color="yellow", alpha=0.5, label="V")

    plt.xlabel("Pixel Intensity (0-100)")
    plt.ylabel("Frequency")
    plt.title("S-V channels Contribution")
    plt.legend()
    plt.show()

def show_image(images_array, index, transformation):
    distorion_array = gain_array = []
    index_true = index-(math.floor(index/len(images_array))*len(images_array))
    image = images_array[index_true]
    obj_image = Image.open(os.path.join(DATASET_PATH, image))
    image_array = np.array(obj_image)
    
    image_trans = transformation(image_array, distorion_array, gain_array, (0.60+(math.floor(index/len(images_array))*0.05)))

    plt.imshow(obj_image)
    plt.title('Original image')
    plt.show()
    plt.imshow(image_trans)
    plt.title('Distorted image')
    plt.show()

    max_energy = compute_power(image_array)
    Pimage = compute_power(image_trans)
    print("power gained: "+str((max_energy-Pimage)/max_energy*100)+"%")
    print("distortion from original: "+str(compute_distortion(image_array, image_trans))+"%")
    return

def show_image_diff(images_array, index, transformation):
    distorion_array = []
    image = images_array[index]
    obj_image = Image.open(os.path.join(DATASET_PATH, image))
    image_array = np.array(obj_image)
    
    image_trans = transformation(image_array, distorion_array, 20)

    plt.imshow(obj_image)
    plt.title('Original image')
    plt.show()
    plt.imshow(image_trans)
    plt.title('Distorted image')
    plt.show()

    max_energy = compute_power(image_array)
    Pimage = compute_power(image_trans)
    print("power gained: "+str((max_energy-Pimage)/max_energy*100)+"%")
    print("distortion from original: "+str(compute_distortion(image_array, image_trans))+"%")
    image_color_contrib(image_array)
    image_color_contrib(image_trans)
    return

def show_image_hist(images_array, index, transformation):
    distorion_array = []
    index_true = index-(math.floor(index/len(images_array))*len(images_array))
    image = images_array[index_true]
    if ( SUBSET ):
        obj_image = Image.open(os.path.join(IMAGE_PATHS_DEBUG, image))
    else:
        obj_image = Image.open(os.path.join(DATASET_PATH, image))
    image_array = np.array(obj_image)
    
    image_trans = transformation(image_array, distorion_array)

    plt.imshow(obj_image)
    plt.title('Original image')
    plt.show()
    plt.imshow(image_trans)
    plt.title('Distorted image')
    plt.show()

    max_energy = compute_power(image_array)
    Pimage = compute_power(image_trans*255)
    print("power gained: "+str((max_energy-Pimage)/max_energy*100)+"%")
    print("distortion from original: "+str(compute_distortion(image_array, image_trans))+"%")
    image_sv_contrib(rgb2hsv(image_array))
    image_sv_contrib(rgb2hsv(image_trans))
    return

def show_image_vs(images_array, index):
    distorion_array = []
    image = images_array[index]
    if ( SUBSET ):
        obj_image = Image.open(os.path.join(IMAGE_PATHS_DEBUG, image))
    else:
        obj_image = Image.open(os.path.join(DATASET_PATH, image))
    image_array = np.array(obj_image)
    
    image_trans = V_S_scale(image_array, distorion_array, 0.8, 1.6)

    plt.imshow(obj_image)
    plt.title('Original image')
    plt.show()
    plt.imshow(image_trans)
    plt.title('Distorted image')
    plt.show()

    max_energy = compute_power(image_array)
    Pimage = compute_power(image_trans*255)
    print("power gained: "+str((max_energy-Pimage)/max_energy*100)+"%")
    print("distortion from original: "+str(compute_distortion(image_array, image_trans))+"%")
    return  

def min_max(distortion_array, power_array):
    if( DEBUG ):
        print("Power")
        print("min gain power: "+str(min(power_array)))
        print("max gain power: "+str(max(power_array)))
        print("Distortion")
        print("min distortion: "+str(min(distortion_array)))
        print("max distortion: "+str(max(distortion_array)))

    pareto = Tranformation_pareto(
        index_of(min(power_array), power_array),
        index_of(max(power_array), power_array),
        index_of(min(distortion_array), distortion_array),
        index_of(max(distortion_array), distortion_array),
    )
    return pareto

def index_of(val, in_list):
    try:
        print(in_list.index(val))
        return in_list.index(val)
    except ValueError:
        return -1 

def compute_power(image_array_rgb):
    Pimage = W0
    for row in image_array_rgb:
        for pixel in row:
            Pimage += WR * pow((pixel[0]),Y) + WG * pow((pixel[1]),Y) + WB * pow((pixel[2]),Y)
    return Pimage

def red_distortion(image_array, distorion_array, const):
    image_low_red = image_array.copy()
    max_energy = compute_power(image_array)
    #0.78 for distortion under 3%
    image_low_red[:,:,0] = (image_array[:,:,0]*const).astype(np.uint8)

    #calcualte the distortion in percentage
    distortion = compute_distortion(image_array, image_low_red)

    Pimage = compute_power(image_low_red)
    if( DEBUG ):
        print("image pw before transformation: "+str(max_energy))
        print("image pw after transformation: "+str(Pimage))

    
    distorion_array.append([distortion,(max_energy-Pimage)/max_energy*100])

    if( DEBUG ):
        print(f"diff gain: {(max_energy-Pimage)/max_energy*100} %")
        print(f"distortion: {distortion} %")
    return image_low_red

def red_distortion_diff(image_array, distorion_array, const):
    image_low_red = image_array.copy()
    max_energy = compute_power(image_array)
    #0.78 for distortion under 3%
    image_low_red[:,:,0] = np.clip(image_array[:,:,0].astype(np.int16) - const, 0, 255).astype(np.uint8)

    #calcualte the distortion in percentage
    distortion = compute_distortion(image_array, image_low_red)
    Pimage = compute_power(image_low_red)

    distorion_array.append([distortion,(max_energy-Pimage)/max_energy*100])

    if( DEBUG ):
        print(f"power gain red_diff: {(max_energy-Pimage)/max_energy*100} %")
        print(f"distortion red_diff: {distortion} %")
    return image_low_red

def blue_distortion(image_array, distorion_array, const):
    image_low_blue = image_array.copy()
    max_energy = compute_power(image_array)
    #0.78 for distortion under 3%
    image_low_blue[:,:,2] = (image_array[:,:,2]*const).astype(np.uint8)

    #calcualte the distortion in percentage
    distortion = compute_distortion(image_array, image_low_blue)

    Pimage = compute_power(image_low_blue)
    if( DEBUG ):
        print("image pw before transformation: "+str(max_energy))
        print("image pw after transformation: "+str(Pimage))

    distorion_array.append([distortion,(max_energy-Pimage)/max_energy*100])
    if( DEBUG ):
        print(f"diff gain: {(max_energy-Pimage)/max_energy*100} %")
        print(f"distortion: {distortion} %")
    return image_low_blue

def blue_distortion_diff(image_array, distorion_array, const):
    image_low_blue = image_array.copy()
    max_energy = compute_power(image_array)
    #0.78 for distortion under 3%
    image_low_blue[:,:,2] = np.clip(image_array[:,:,2].astype(np.int16) - const, 0, 255).astype(np.uint8)

    #calculate the distortion in percentage
    distortion = compute_distortion(image_array, image_low_blue)
    Pimage = compute_power(image_low_blue)
    
    distorion_array.append([distortion,(max_energy-Pimage)/max_energy*100])
    if( DEBUG ):
        print(f"diff gain: {(max_energy-Pimage)/max_energy*100} %")
        print(f"distortion: {distortion} %")
    return image_low_blue

def hist_eq_S(image_array, distortion_array):
    max_energy = compute_power(image_array)

    image_array_eq_s = image_array.copy()
    image_array_hsv = rgb2hsv(image_array_eq_s)
    image_array_hsv[:, :, 1] = equalize_hist(image_array_hsv[:, :, 1])
    image_array_eq_s_rgb = hsv2rgb(image_array_hsv)

    distortion = compute_distortion(image_array_eq_s, image_array_eq_s_rgb)
    Pimage = compute_power(image_array_eq_s_rgb*255)
    distortion_array.append([distortion,(max_energy-Pimage)/max_energy*100])

    if( DEBUG ):
        print(f"diff gain: {(max_energy-Pimage)/max_energy*100} %")
        print(f"distortion: {distortion} %")

    return image_array_eq_s_rgb

def hist_eq_V(image_array, distortion_array):
    
    max_energy = compute_power(image_array)

    image_array_eq_s = image_array.copy()
    image_array_hsv = rgb2hsv(image_array_eq_s)
    image_array_hsv[:, :, 2] = equalize_hist(image_array_hsv[:, :, 2])
    image_array_eq_s_rgb = hsv2rgb(image_array_hsv)

    distortion = compute_distortion(image_array_eq_s, image_array_eq_s_rgb)
    Pimage = compute_power(image_array_eq_s_rgb*255)
    distortion_array.append([distortion,(max_energy-Pimage)/max_energy*100])

    if( DEBUG ):
        print(f"diff gain: {(max_energy-Pimage)/max_energy*100} %")
        print(f"distortion: {distortion} %")

    return image_array_eq_s_rgb

def S_scale(image_array, distortion_array, scale):
    #Increasing the saturation of the pixel color the color should be darker and so the power should decrease
    max_energy = compute_power(image_array)

    image_array_eq_s = image_array.copy()
    image_array_hsv = rgb2hsv(image_array_eq_s)
    image_array_hsv[:, :, 1] = np.clip(image_array_hsv[:,:,1] * scale , 0, 1).astype(np.float64)
    image_array_eq_s_rgb = hsv2rgb(image_array_hsv)

    distortion = compute_distortion(image_array_eq_s, image_array_eq_s_rgb)
    Pimage = compute_power(image_array_eq_s_rgb*255)
    distortion_array.append([distortion,(max_energy-Pimage)/max_energy*100])
    
    if( DEBUG ):
        print(f"diff gain: {(max_energy-Pimage)/max_energy*100} %")
        print(f"distortion: {distortion} %")

    return image_array_eq_s_rgb

def V_scale(image_array, distortion_array, scale):
    #make the pixel value darker so it has to decrease the total power
    max_energy = compute_power(image_array)

    image_array_eq_s = image_array.copy()
    image_array_hsv = rgb2hsv(image_array_eq_s)
    # print(type(image_array_hsv[0, 0, 2]))
    # print(image_array_hsv)
    image_array_hsv[:, :, 2] = np.clip(image_array_hsv[:,:,2] * scale , 0, 1).astype(np.float64)
    image_array_eq_s_rgb = hsv2rgb(image_array_hsv)

    distortion = compute_distortion(image_array_eq_s, image_array_eq_s_rgb)
    Pimage = compute_power(image_array_eq_s_rgb*255)
    distortion_array.append([distortion,(max_energy-Pimage)/max_energy*100])
    
    if( DEBUG ):
        print(f"diff gain: {(max_energy-Pimage)/max_energy*100} %")
        print(f"distortion: {distortion} %")

    return image_array_eq_s_rgb

def V_S_scale(image_array, distortion_array, scale_v, scale_s):
    #combine two of the most power saving strategies
    max_energy = compute_power(image_array)

    image_array_eq_s = image_array.copy()
    image_array_hsv = rgb2hsv(image_array_eq_s)

    image_array_hsv[:, :, 2] = np.clip(image_array_hsv[:,:,2] * scale_v , 0, 1).astype(np.float64)
    image_array_hsv[:, :, 1] = np.clip(image_array_hsv[:,:,1] * scale_s , 0, 1).astype(np.float64)
    image_array_eq_s_rgb = hsv2rgb(image_array_hsv)

    distortion = compute_distortion(image_array_eq_s, image_array_eq_s_rgb)
    Pimage = compute_power(image_array_eq_s_rgb*255)
    distortion_array.append([distortion,(max_energy-Pimage)/max_energy*100])
    
    if( DEBUG ):
        print(f"diff gain: {(max_energy-Pimage)/max_energy*100} %")
        print(f"distortion: {distortion} %")
    return image_array_eq_s_rgb

def compute_distortion(original_image, processed_image):
    original_image_lab = rgb2lab(original_image)
    processed_image_lab = rgb2lab(processed_image)

    distortion = 0
    distortion_img = original_image_lab -processed_image_lab
    
    for row in distortion_img:
        for pixel in row:
            distortion += pow((pow(pixel[0],2)+pow(pixel[1],2)+pow(pixel[2],2)),1/2)
    
    max_distortion = original_image.shape[0]*original_image.shape[1]*pow((pow(100,2)+pow(255,2)+pow(255,2)),1/2)

    return (distortion/max_distortion)*100

#day 2 DVS
def compute_pixel_current(Drgb, Vdd=15):#Drgb = [r,g,b]
    Icell = ((P1 * Vdd * Drgb)/255)+((P2*Drgb)/255)+P3
    return Icell

def compute_panel_power(image_rgb, Vdd=15):
    Ppanel = 0
    for row in image_rgb:
        for pixel in row:
            rgb = compute_pixel_current(pixel, Vdd)
            Ppanel += rgb[0]+rgb[1]+rgb[2]
    Ppanel = Ppanel * Vdd

    return Ppanel

def compute_panel_power_diff(image_orig, Vdd_orig=15, image_trans=[], Vdd_trans=15):
    return (compute_panel_power(image_orig, Vdd_orig)-compute_panel_power(image_trans, Vdd_trans))/compute_panel_power(image_orig, Vdd_orig)*100

def displayed_image(
        i_cell: np.ndarray,
        vdd: float,
        p1: float = 4.251e-5,
        p2: float = -3.029e-4,
        p3: float = 3.024e-5,
        orig_vdd: float = 15,
        ) -> Tuple[np.ndarray, np.ndarray]:
    """
    Display an image on the OLED display taking into account the effect of DVS.

    :param i_cell: An array of the currents drawn by each pixel of the display.
    :param vdd: The new voltage of the display.
    """
    i_cell_max = (p1 * vdd * 1) + (p2 * 1) + p3
    image_rgb_max = (i_cell_max - p3) / (p1 * orig_vdd + p2) * 255
    out = np.round((i_cell - p3) / (p1 * orig_vdd + p2) * 255)
    original_image = out.copy()

    # Clip the values exceeding `i_cell_max` to `image_rgb_max`
    out[i_cell > i_cell_max] = image_rgb_max
    
    max_energy = compute_panel_power(original_image, orig_vdd)
    Pimage = compute_panel_power(out, vdd)
    power_gained = (max_energy-Pimage)/max_energy*100

    return original_image.astype(np.uint8), out.astype(np.uint8), power_gained

def V_scale_b(image_array, scale):
    #make the pixel value darker so it has to decrease the total power

    #print(scale)
    image_array_eq_s = image_array.copy()
    image_array_hsv = rgb2hsv(image_array_eq_s)
    
    image_array_hsv[:, :, 2] = np.clip(image_array_hsv[:,:,2] * scale , 0, 1).astype(np.float64)
    image_array_eq_s_rgb = hsv2rgb(image_array_hsv)

    return image_array_eq_s_rgb

def V_sum_b(image_array, scale):
    #make the pixel value darker so it has to decrease the total power

    #print(scale)
    image_array_eq_s = image_array.copy()
    image_array_hsv = rgb2hsv(image_array_eq_s)
    
    image_array_hsv[:, :, 2] = np.clip(image_array_hsv[:,:,2] + scale , 0, 1).astype(np.float64)
    image_array_eq_s_rgb = hsv2rgb(image_array_hsv)

    return image_array_eq_s_rgb

def S_scale_b(image_array, scale):
    #make the pixel value darker so it has to decrease the total power
    max_energy = compute_power(image_array)

    image_array_eq_s = image_array.copy()
    image_array_hsv = rgb2hsv(image_array_eq_s)
    # print(type(image_array_hsv[0, 0, 2]))
    # print(image_array_hsv)
    image_array_hsv[:, :, 1] = np.clip(image_array_hsv[:,:,1] * scale , 0, 1).astype(np.float64)
    image_array_eq_s_rgb = hsv2rgb(image_array_hsv)

    distortion = compute_distortion(image_array_eq_s, image_array_eq_s_rgb)
    Pimage = compute_panel_power(image_array_eq_s_rgb*255)
    
    power_gained = (max_energy-Pimage)/max_energy*100

    return power_gained, distortion, image_array_eq_s_rgb