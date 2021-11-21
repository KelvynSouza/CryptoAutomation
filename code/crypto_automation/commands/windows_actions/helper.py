import win32api, win32con, win32gui
from win32con import *
import pyautogui
import subprocess
import numpy as np
from crypto_automation.commands.shared.numbers_helper import random_waitable_number, random_number_between

class WindowsActionsHelper:
    def __init__(self, config):
        self.__config = config
        

    def click_on(self, x, y, number_clicks = 1):
        pyautogui.click(x=x, y=y, clicks=number_clicks, interval=0.25, button='left')
    

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
        pyautogui.typewrite(text, interval=random_number_between(0.3, 0.6))


    def press_special_buttons(button):
        pyautogui.press(button)


    def take_screenshot():
        image = pyautogui.screenshot()
        return np.array(image)


    def check_position_on_screen(self, x, y):
        return pyautogui.onScreen(x, y)


    def open_and_maximise_front_window(self, program_path, *arguments):   
        args = [program_path]
        args.extend(arguments)
        process = subprocess.Popen(args)
        process.wait()     
        hwnd = win32gui.GetForegroundWindow()
        win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)

    