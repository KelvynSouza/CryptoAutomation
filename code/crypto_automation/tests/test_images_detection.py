import cv2
import numpy as np
import pyautogui
from matplotlib import pyplot as plt
from crypto_automation.commands.image_processing.helper import ImageHelper


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

image_path = "../resources/images/test/heroes_list.png"
template_path = "../resources/images/game/work_button.png"

image = cv2.imread(image_path) 
template = cv2.imread(template_path) 

imgray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
ret, thresh = cv2.threshold(imgray, 200, 255, 0)
contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
cv2.drawContours(thresh, contours, -1, (0,255,0), 3)

show_info(thresh, True)

#list_hero = cv2.cvtColor(list_hero, cv2.COLOR_RGB2GRAY)

points = image_helper.find_exact_matches_position(image, template, False, 0.05)

for x, y in points:
    cv2.circle(image, (x, y), 5, (255,0,0), 3)
    
show_info(image)
print('Final')

