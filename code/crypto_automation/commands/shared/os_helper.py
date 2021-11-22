import os
import subprocess
import win32api, win32con, win32gui 


def create_log_folder(dirName):
    try:
        os.mkdir("log")
        print("Directory " , dirName ,  " Created ") 
    except FileExistsError:
        print("Directory " , dirName ,  " already exists")


def execute_system_command(commands:list):
    return subprocess.run(commands)
