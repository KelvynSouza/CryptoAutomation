import os
def create_log_folder(dirName):
    try:
        os.mkdir("log")
        print("Directory " , dirName ,  " Created ") 
    except FileExistsError:
        print("Directory " , dirName ,  " already exists")