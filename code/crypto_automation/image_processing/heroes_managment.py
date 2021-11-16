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

heroes_list_image = "../images/test/error_screen.png"
work_button_template = "../images/ok_button.png"

list_hero = cv2.imread(heroes_list_image) 
template = cv2.imread(work_button_template) 

points = image_helper.find_exact_matches_position(list_hero, template,0.05)

for x, y in points:
    cv2.circle(list_hero, (x, y),30,(255,0,0), 3)
    
show_info(list_hero)
print('Final')

