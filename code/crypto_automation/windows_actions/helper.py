import win32api, win32con
from win32con import *
import pyautogui, sys


class WindowsActionsHelper:
    def __init__(self, config):
        self.__config = config
        
    def __click_and_scroll_down_from_package(self, x, y):
        pyautogui.scroll(self.__config['IMAGEDETECTION'].getint('scroll_intensity'), x=x, y=y)
    

    def __click_and_drag(self, from_x, from_y, height = 0, width=0):
        pyautogui.moveTo(from_x, from_y, 2)
        pyautogui.drag(height, width, 2, button='left')

    
    def click_and_scroll_down(self, x, y):
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x, y,0,0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x, y,0,0)   
        for x in range(self.__config['IMAGEDETECTION'].getint('scroll_intensity')):  
            win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, -1, 0)