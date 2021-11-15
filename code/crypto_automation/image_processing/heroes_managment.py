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

heroes_list_image = "../images/test/heroes_list.png"
work_button_template = "../images/work_button.png"

list_hero = cv2.imread(heroes_list_image) 
template = cv2.imread(work_button_template) 

points = image_helper.find_exact_matches_position(list_hero, template)


print('Final')

