import cv2
import numpy as np
import pyautogui
from matplotlib import pyplot as plt
from app.shared.image_processing_helper import ImageHelper


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

def take_screenshot():
    image_np = np.array(pyautogui.screenshot())
    return image_np[:, :, ::-1].copy() 


image_helper = ImageHelper()

image_path = "../resources/images/test/map_mode.png"
template_path = "../resources/images/game/sleep_balloon2.png"

image = cv2.imread(image_path) 
template = cv2.imread(template_path)
show_info(template)


points = image_helper.find_exact_matches_position(image, template, False, 0.30)

for x, y in points:
    cv2.circle(image, (x, y), 5, (255,0,0), 3)
    
show_info(image)
print('Final')
