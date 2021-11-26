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

#image = "../resources/images/test/new_map.png"
template_path = "../resources/images/game/treasure_chest_icon.png"

list_hero = take_screenshot()
#template = cv2.imread(template) 

#list_hero = cv2.cvtColor(list_hero, cv2.COLOR_RGB2GRAY)

points = image_helper.wait_all_until_match_is_found(take_screenshot, [], template_path, 2, 0.01, should_grayscale=False)

for x, y in points:
    cv2.circle(list_hero, (x, y), 5, (255,0,0), 3)
    
show_info(list_hero)
print('Final')
