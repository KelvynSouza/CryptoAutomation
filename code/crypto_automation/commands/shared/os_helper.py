import os
import subprocess


def create_log_folder(dirName, screenshot_path):
    try:
        os.mkdir("log")
        print("Directory " , dirName ,  " Created ") 
    except FileExistsError:
        print("Directory " , dirName ,  " already exists")

    try:
        os.mkdir(screenshot_path)
        print("Directory " , screenshot_path ,  " Created ") 
    except FileExistsError:
        print("Directory " , screenshot_path ,  " already exists")


def execute_system_command(commands:list):
    return subprocess.run(commands)
