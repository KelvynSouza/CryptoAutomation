import os
import subprocess
import random

def create_log_folder(dirName):
    try:
        os.mkdir("log")
        print("Directory " , dirName ,  " Created ") 
    except FileExistsError:
        print("Directory " , dirName ,  " already exists")


def execute_system_command(commands:list):
    return subprocess.run(commands)


def random_waitable_number(config):
    return random.uniform(config['COMMON']['random_waits_from'], config['COMMON']['random_waits_to'])


def random_number_between(min, max):
    return random.uniform(min, max)