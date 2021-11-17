import cv2
import numpy as np
from matplotlib import pyplot as plt
from helper import ImageHelper


#region Util
def show_info(image, isgray=False):
    print('-----------------------------------------------------')    
    print('shape:', image.shape, 'and', 'size:', image.size)    
    print(image.dtype)
    if isgray:
        plt.imshow(image, cmap='gray')        
    else:
        plt.imshow(image[:,:,::-1])
    plt.show()
    


#endregion

image_helper = ImageHelper()

image = "../images/test/error_screen.png"
template = "../images/map_screen_validator.png"

list_hero = cv2.imread(image) 
template = cv2.imread(template) 

points = image_helper.find_exact_matches_position(list_hero, template,0.05)

for x, y in points:
    cv2.circle(list_hero, (x, y),30,(255,0,0), 3)
    
show_info(list_hero)
print('Final')

