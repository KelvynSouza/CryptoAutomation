import threading
import time
from crypto_automation.app.shared.numbers_helper import random_number_between


class Job(threading.Thread):
    def __init__(self, t, retrytime, run_once=False, random_timer=False, *args, **kwargs):
        super(Job, self).__init__()
        self.__target = t  
        self.__args = args
        self.__kwargs =  kwargs  

        self.__run_once = run_once
        self.__retrytime = retrytime
        self.__random_timer = random_timer
        self.__flag = threading.Event() # The flag used to pause the thread
        self.__flag.set() # Set to True
        self.__running = threading.Event() # Used to stop the thread identification
        self.__running.set() # Set running to True 


    def run(self):
        while self.__running.isSet():
            if self.__target:                
                self.__target(*self.__args, **self.__kwargs)
            else:
                raise Exception("Method not found for thread!")
                
            random_number = random_number_between(1.0, 2) if self.__random_timer == True else 1
            time.sleep(self.__retrytime*random_number)

            self.__flag.wait() # return immediately when it is True, block until the internal flag is True when it is False

            if self.__run_once:
                break


    def pause(self):
        self.__flag.clear() # Set to False to block the thread


    def resume(self):
        self.__flag.set() # Set to True, let the thread stop blocking


    def stop(self):
        self.__flag.set() # Resume the thread from the suspended state, if it is already suspended
        self.__running.clear() # Set to False
