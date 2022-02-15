import cv2
import numpy as np
import pyautogui
from matplotlib import pyplot as plt
from crypto_automation.app.shared.image_processing_helper import ImageHelper


#region Util
def show_info(image, original=False, image_name = "Imagem"):
        print('-----------------------------------------------------')  
        print(image_name)  
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
#endregion

def take_screenshot():
    image_np = np.array(pyautogui.screenshot())
    return image_np[:, :, ::-1].copy() 


image_helper = ImageHelper()

image_path = "../resources/images/test/luna/heroes_active_empty_energy_screen.png"
template_path = "../resources/images/luna/low_energy_bar_checked.png"

image = cv2.imread(image_path)

template = cv2.imread(template_path)

points = image_helper.find_exact_matches_position(image, template, False, 0.1)

for (x,y) in points:
    cv2.circle(image, (x, y), 5, (255,0,0), 3)
    print(f"found point in x: {x}, y: {y}")
    
show_info(image)
print('Final')
