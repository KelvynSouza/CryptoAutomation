import win32api, win32con, win32gui
import pyautogui
import cv2 
import subprocess
import os
import numpy as np
from datetime import datetime
from win32con import *
from crypto_automation.commands.image_processing.helper import ImageHelper
from crypto_automation.commands.shared.numbers_helper import random_waitable_number, random_number_between
from random import randrange


class WindowsActionsHelper:
    def __init__(self, config, image_helper: ImageHelper = None):
        self.__config = config
        self.__image_helper = image_helper
        #pyautogui.FAILSAFE = False

    
    def move_to(self, x, y):
        pyautogui.moveTo(x, y, random_waitable_number(self.__config), self.__random_tween())


    def __random_tween(self):
        random_number = randrange(1, 30)
        if random_number == 1: return pyautogui.easeInQuad 
        if random_number == 2: return pyautogui.easeOutQuad 
        if random_number == 3: return pyautogui.easeInOutQuad 
        if random_number == 4: return pyautogui.easeInCubic 
        if random_number == 5: return pyautogui.easeOutCubic 
        if random_number == 6: return pyautogui.easeInOutCubic 
        if random_number == 7: return pyautogui.easeInQuart 
        if random_number == 8: return pyautogui.easeOutQuart 
        if random_number == 9: return pyautogui.easeInOutQuart 
        if random_number == 10: return pyautogui.easeInQuint
        if random_number == 11: return pyautogui.easeOutQuint
        if random_number == 12: return pyautogui.easeInOutQuint 
        if random_number == 13: return pyautogui.easeInSine 
        if random_number == 14: return pyautogui.easeOutSine 
        if random_number == 15: return pyautogui.easeInOutSine 
        if random_number == 16: return pyautogui.easeInExpo
        if random_number == 17: return pyautogui.easeOutExpo 
        if random_number == 18: return pyautogui.easeInOutExpo 
        if random_number == 19: return pyautogui.easeInCirc 
        if random_number == 20: return pyautogui.easeOutCirc 
        if random_number == 21: return pyautogui.easeInOutCirc 
        if random_number == 22: return pyautogui.easeInElastic 
        if random_number == 23: return pyautogui.easeOutElastic 
        if random_number == 24: return pyautogui.easeInOutElastic
        if random_number == 25: return pyautogui.easeInBack 
        if random_number == 26: return pyautogui.easeOutBack 
        if random_number == 27: return pyautogui.easeInOutBack 
        if random_number == 28: return pyautogui.easeInBounce 
        if random_number == 29: return pyautogui.easeOutBounce 
        if random_number == 30: return pyautogui.easeInOutBounce
        

    def click_on(self, x, y):
        self.move_to(x, y)
        self.__click(x,y)
    

    def __click_and_scroll_down_from_package(self, x, y):
        self.click_on(x, y)
        pyautogui.scroll(self.__config['IMAGEDETECTION'].getint('scroll_intensity'), x=x, y=y)    
    
    
    def click_and_scroll_down(self, x, y):
        self.__click(x,y)
        for x in range(self.__config['IMAGEDETECTION'].getint('scroll_intensity')):  
            win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, -1, 0)


    def click_and_hold(self, x, y):
        self.move_to(x, y)
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y,0,0) 


    def move_click_hold(self, x, y):
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y,0,0) 


    def release_click(self, x, y):           
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x, y,0,0)  


    def __click(self, x, y):
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x, y,0,0)        
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x, y,0,0)   


    def rumble_mouse(self):
        pyautogui.moveRel(40, 0, duration=0.2)
        pyautogui.moveRel(-80, 0, duration=0.2)
        pyautogui.moveRel(40, 0, duration=0.2)
        pyautogui.click()



    def write_at(self, x, y, text):
        self.click_on(x, y)
        pyautogui.typewrite(text, interval=random_number_between(0.1, 0.4))


    def press_special_buttons(self, button):
        pyautogui.press(button)


    def take_screenshot(self):
        image_np = np.array(pyautogui.screenshot())
        return image_np[:, :, ::-1].copy()  
        

    def save_screenshot_log(self, grayscale = True, original_resolution = False):
        image = self.take_screenshot()
        if original_resolution == False:
            image = self.__image_helper.rescale_frame(image, 50 ,convert_grayscale=grayscale)         
        date_time = datetime.now().strftime("%Y-%m-%d %H_%M_%S")
        screenshot_path = os.path.join( self.__config['COMMON']['screenshots_path'], date_time+'.png')
        cv2.imwrite(screenshot_path, image)


    def check_position_on_screen(self, x, y):
        return pyautogui.onScreen(x, y)


    def open_and_maximise_front_window(self, program_path, image_validation_path, *arguments):   
        args = [program_path]
        args.extend(arguments)
        startupinf = subprocess.STARTUPINFO()
        # {"hide":0, "normal":1, "minimized":2,"maximized":3,"hidden":0,"minimize":2,"maximize":3}
        startupinf.wShowWindow = 3 
        subprocess.Popen(args, startupinfo=startupinf)  
        self.__image_helper.wait_until_match_is_found(self.take_screenshot, 
                                                [], image_validation_path, 
                                                    self.__config['TIMEOUT'].getint('imagematching'), 
                                                    0.05, True)       


    def process_exists(self, process_name): 
        if process_name == "":
            return False

        call = 'tasklist | findstr ' + process_name    
        output = subprocess.Popen(call, shell=True,  stdout=subprocess.PIPE, text=True)
        stdout, _ = output.communicate() 
        
        last_line = stdout.strip().split('K\n')[-1]        
        return last_line.lower().startswith(process_name.lower())
       

    def kill_process(self, process_name):
        subprocess.call("taskkill /im "+process_name+" /F")
        
