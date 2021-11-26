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

ret, thresh = cv2.threshold(imgray, 225, 240, cv2.THRESH_BINARY)

#show_info(thresh, True)

edg_img = cv2.Canny(thresh, 225, 240)

#show_info(edg_img, True)

#ret, thresh = cv2.threshold(imgray, 225, 255, 0)
contours, hierarchy = cv2.findContours(edg_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


for contour in contours:
    (x,y,w,h) = cv2.boundingRect(contour)
    if(w > 400 and (h > 50 and h < 200)):
        cv2.rectangle(image, (x, y), (x + w, y + h), (225, 255, 0), 2)

show_info(image)

'''
list_hero = cv2.cvtColor(list_hero, cv2.COLOR_RGB2GRAY)

points = image_helper.find_exact_matches_position(image, template, True, 0.05)

for x, y in points:
    cv2.circle(image, (x, y), 5, (255,0,0), 3)
    
show_info(image)
print('Final')
'''