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


class WindowsActionsHelper:
    def __init__(self, config, image_helper: ImageHelper = None):
        self.__config = config
        self.__image_helper = image_helper
        

    def click_on(self, x, y, number_clicks = 1):
        pyautogui.click(x=x, y=y, clicks=number_clicks, interval=0.25, button='left', duration=random_waitable_number(self.__config))
    

    def click_and_drag(self, from_x, from_y, height = 0, width=0):
        pyautogui.moveTo(from_x, from_y, random_waitable_number(self.__config))
        pyautogui.drag(height, width, random_waitable_number(self.__config), button='left')


    def __click_and_scroll_down_from_package(self, x, y):
        self.click_on(x, y)
        pyautogui.scroll(self.__config['IMAGEDETECTION'].getint('scroll_intensity'), x=x, y=y)    

    
    def click_and_scroll_down(self, x, y):
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x, y,0,0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x, y,0,0)   
        for x in range(self.__config['IMAGEDETECTION'].getint('scroll_intensity')):  
            win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, -1, 0)


    def write_at(self, x, y, text):
        self.click_on(x, y)
        pyautogui.typewrite(text, interval=random_number_between(0.1, 0.4))


    def press_special_buttons(self, button):
        pyautogui.press(button)


    def take_screenshot(self):
        image_np = np.array(pyautogui.screenshot())
        return image_np[:, :, ::-1].copy()  
        

    def save_screenshot_log(self, grayscale = True):
        image = self.take_screenshot()
        image = self.__image_helper.rescale_frame(image, convert_grayscale=grayscale)         
        date_time = datetime.now().strftime("%Y-%m-%d %H_%M_%S")
        screenshot_path = os.path.join( self.__config['COMMON']['screenshots_path'], date_time+'.png')
        cv2.imwrite(screenshot_path, image)


    def check_position_on_screen(self, x, y):
        return pyautogui.onScreen(x, y)


    def open_and_maximise_front_window(self, program_path, image_validation_path, *arguments):   
        args = [program_path]
        args.extend(arguments)
        subprocess.Popen(args)  
        self.__image_helper.wait_until_match_is_found(self.take_screenshot, 
                                                [], image_validation_path, 
                                                    self.__config['TIMEOUT'].getint('imagematching'), 
                                                    0.05, True)
        hwnd = win32gui.GetForegroundWindow()
        win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)


    def process_exists(self, process_name): 
        if process_name == "":
            return False

        call = 'tasklist | findstr ' + process_name    
        output = subprocess.Popen(call, shell=True,  stdout=subprocess.PIPE, text=True)
        stdout, _ = output.communicate() 
        
        last_line = stdout.strip().split('K\n')[-1]        
        return last_line.lower().startswith(process_name.lower())
       

    def kill_process(self, process_name):
        subprocess.call("taskkill /im "+process_name)
        
