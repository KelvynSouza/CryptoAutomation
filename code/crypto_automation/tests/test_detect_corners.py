import cv2
import numpy as np
import pyautogui
from matplotlib import pyplot as plt
from crypto_automation.commands.image_processing.helper import ImageHelper


def show_info(image, original=False):
    print('-----------------------------------------------------')    
    print('shape:', image.shape, 'and', 'size:', image.size)    
    print(image.dtype)
    if original:
        plt.imshow(image)
    else:
        if len(image.shape) < 3:
            plt.imshow(image, cmap='gray')        
        else:
            plt.imshow(image[:,:,::-1])
    
    plt.show()

def take_screenshot():
    image_np = np.array(pyautogui.screenshot())
    return image_np[:, :, ::-1].copy() 

def getting_rectangle_countours(image_treated, h_min = None, h_max = None, w_min = None, w_max = None):
    contours, _ = cv2.findContours(image_treated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if h_min:
        h_min_fuction = lambda h: h >= h_min
    else:
        h_min_fuction = lambda h: True

    if h_max:
        h_max_fuction = lambda h: h <= h_max
    else:
        h_max_fuction = lambda h: True

    if w_min:
        w_min_fuction = lambda w: w >= w_min
    else:
        w_min_fuction = lambda w: True

    if w_max:
        w_max_fuction = lambda w: w <= w_max
    else:
        w_max_fuction = lambda w: True
    
    valid_contours = list()
    for contour in contours:
        (x,y,w,h) = cv2.boundingRect(contour)
        if (w_min_fuction(w) and w_max_fuction(w)) and (h_min_fuction(h) and h_max_fuction(h)):
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
show_info(thresh)
show_info(edg_img)

#find countours, try to find just the externa contours in the hierarchy
contours = getting_rectangle_countours(edg_img, 50, 200, 400)
#image = draw_rectangles_in_image(image, contours)

#show_info(image)

#cut hero from list
heroes_cropped = list()
for x,y,w,h in contours:
    cropped = image[y:y+h, x:x+w]
    heroes_cropped.append((cropped, (x,y,w,h)))

#analyze hero stamina
if(heroes_cropped):
    for hero, position in heroes_cropped:
        hero_to_check = hero
        show_info(hero_to_check)
        hero_gray = cv2.cvtColor(hero_to_check, cv2.COLOR_BGR2GRAY)
        ret, thresh_hero = cv2.threshold(hero_gray, 100, 120, cv2.THRESH_BINARY)
        edg_img = cv2.Canny(thresh_hero, 225, 255)    
        show_info(thresh_hero)
        contours = getting_rectangle_countours(edg_img, 10, 20, 100)
        
        if contours:
            x,y,w,h = contours[0]
            hero_stamina = hero_to_check[y:y+h, x:x+w] 
            show_info(hero_stamina) 
            # Threshold of green 
            lower_green = np.array([57, 157, 120])
            upper_green = np.array([190, 226, 181])
            
            # Detection in binary
            mask = cv2.inRange(hero_stamina, lower_green, upper_green)            
            show_info(mask) 

            if np.max(mask) == 0:
                # Threshold of red
                lower_red = np.array([39, 43, 196])
                upper_red = np.array([103, 139, 254])
                mask = cv2.inRange(hero_stamina, lower_red, upper_red)                

            _,_,charged_bar_w,_ = getting_rectangle_countours(mask, None, None, None, None)[0] 

            cv2.putText(image, f'{charged_bar_w}%', (position[0]+100, position[1]), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
            
            print(charged_bar_w)
    show_info(image)

