import win32api, win32con
from win32con import *
import pyautogui, sys
import numpy as np
from crypto_automation.commands.shared.os_helper import random_waitable_number

class WindowsActionsHelper:
    def __init__(self, config):
        self.__config = config
        

    def click_on(self, x, y):
        pyautogui.click(x=x, y=y, clicks=1, interval=random_waitable_number(self.__config), button='left')
    

    def click_and_drag(self, from_x, from_y, height = 0, width=0):
        pyautogui.moveTo(from_x, from_y, 2)
        pyautogui.drag(height, width, 2, button='left')


    def __click_and_scroll_down_from_package(self, x, y):
        pyautogui.scroll(self.__config['IMAGEDETECTION'].getint('scroll_intensity'), x=x, y=y)    

    
    def click_and_scroll_down(self, x, y):
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x, y,0,0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x, y,0,0)   
        for x in range(self.__config['IMAGEDETECTION'].getint('scroll_intensity')):  
            win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, -1, 0)


    def write_at(self, x, y, text):
        self.click_on(x, y)
        pyautogui.typewrite(text, interval=0.5)


    def take_screenshot():
        image = pyautogui.screenshot()
        return np.array(image)


    def check_position_on_screen(self, x, y):
        return pyautogui.onScreen(x, y)

    