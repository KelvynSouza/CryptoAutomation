import win32api, win32con
from win32con import *

class WindowsActionsHelper:
    def __init__(self, config):
        self.__config = config
        
    def click_and_scroll_down(self, x, y):
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x, y,0,0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x, y,0,0)   
        for x in range(self.__config['IMAGEDETECTION'].getint('scroll_intensity')):  
            win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, -1, 0)