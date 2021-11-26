import cv2
import numpy as np
import pyautogui
from matplotlib import pyplot as plt
from crypto_automation.commands.image_processing.helper import ImageHelper


#region Util
def show_info(image, original=False):
    print('-----------------------------------------------------')    
    print('shape:', image.shape, 'and', 'size:', image.size)    
    print(image.dtype)
    if len(image.shape) < 3:
        plt.imshow(image, cmap='gray')        
    else:
        plt.imshow(image[:,:,::-1])
    if original:
        plt.imshow(image)
    plt.show()
#endregion

def take_screenshot():
    image_np = np.array(pyautogui.screenshot())
    return image_np[:, :, ::-1].copy() 

def getting_rectangle_countours(image_treated, h_min, h_max, w_min):
    contours, _ = cv2.findContours(image_treated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    valid_contours = list()
    for contour in contours:
        (x,y,w,h) = cv2.boundingRect(contour)
        if(w > w_min and (h > h_min and h < h_max)):
            valid_contours.append((x,y,w,h))
    
    return valid_contours

def draw_rectangles_in_image(image, contours):
    for x,y,w,h in contours:
        cv2.rectangle(image, (x, y), (x + w, y + h), (225, 255, 0), 2)
    return image

image_helper = ImageHelper()

image_path = "../resources/images/test/heroes_list.png"

image = cv2.imread(image_path) 

#treat image for better detection of edges
imgray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
ret, thresh = cv2.threshold(imgray, 225, 240, cv2.THRESH_BINARY)
edg_img = cv2.Canny(thresh, 225, 240)

#find countours, try to find just the externa contours in the hierarchy
contours = getting_rectangle_countours(edg_img, 50, 200, 400)

#image = draw_rectangles_in_image(image, contours)

#cut hero from list
heroes_cropped = list()
for x,y,w,h in contours:
    cropped = image[y:y+h, x:x+w]
    heroes_cropped.append(cropped)

#analyze hero stamina
if(heroes_cropped):
    hero_to_check = heroes_cropped[0]

    hero_gray = cv2.cvtColor(hero_to_check, cv2.COLOR_BGR2GRAY)
    ret, thresh_hero = cv2.threshold(hero_gray, 120, 200, cv2.THRESH_BINARY)
    edg_img = cv2.Canny(thresh_hero, 225, 255)    

    contours = getting_rectangle_countours(edg_img, 10, 40, 100)
    #hero_to_check = draw_rectangles_in_image(hero_to_check, contours)
    #show_info(hero_to_check)

    if(contours):
        x,y,w,h = contours[0]
        hero_stamina = hero_to_check[y:y+h, x:x+w]
        show_info(hero_stamina, True)

        # Threshold of green in HSV space
        lower_green = np.array([57,157,120])
        upper_green = np.array([190, 226, 177])
    
        # preparing the mask to overlay
        mask = cv2.inRange(hero_stamina, lower_green, upper_green)
        show_info(mask)


        '''
        #Use of threshold
        hero_stamina_gray = cv2.cvtColor(hero_stamina, cv2.COLOR_BGR2GRAY)   
        show_info(hero_stamina_gray)     

        ret, thresh_hero_stamina = cv2.threshold(hero_stamina_gray, 170, 255,  cv2.THRESH_OTSU)
        show_info(thresh_hero_stamina)

        ret, thresh_hero_stamina_add = cv2.threshold(hero_stamina_gray, 170, 255, cv2.THRESH_BINARY_INV)
        show_info(thresh_hero_stamina_add)

        show_info(thresh_hero_stamina+thresh_hero_stamina_add)
        '''
        print()

