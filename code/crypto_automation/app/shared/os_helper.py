import os
import subprocess


def create_folder(folder_path):
    try:
        os.mkdir(folder_path)
        print("Directory " , folder_path ,  " Created ") 
    except FileExistsError:
        print("Directory " , folder_path ,  " already exists")
        

def execute_system_command(commands:list):
    return subprocess.run(commands)
