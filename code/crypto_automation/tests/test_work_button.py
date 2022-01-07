import configparser
import threading
import time
from app.commands.game_status_manager import GameStatusManager
from app.shared.image_processing_helper import ImageHelper
from app.shared.numbers_helper import random_waitable_number
from app.shared.os_helper import create_folder
from app.shared.windows_action_helper import WindowsActionsHelper


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

image_path = "../resources/images/test/heroes_list_resting.png"
template_path = "../resources/images/game/work_button.png"

image = cv2.imread(image_path) 
template = cv2.imread(template_path)

points = image_helper.find_exact_matches_position(image, template, False, 0.005)

create_folder(config['COMMON']['log_folder_path'])
create_folder(config['COMMON']['screenshots_path'])

asd = test(config)
asd.run()
