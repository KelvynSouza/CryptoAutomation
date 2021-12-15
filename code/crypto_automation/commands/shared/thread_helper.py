import threading
import time
from crypto_automation.commands.shared.numbers_helper import random_number_between


class Job(threading.Thread):
    def __init__(self, t, retrytime, *args, **kwargs):        
        super(Job, self).__init__(target=t, *args, **kwargs)
        self.__retrytime = retrytime
        self.__flag = threading.Event() # The flag used to pause the thread
        self.__flag.set() # Set to True
        self.__running = threading.Event() # Used to stop the thread identification
        self.__running.set() # Set running to True        
        self.start()


    def start(self):
        while self.__running.isSet():           
            super().run()          
            time.sleep(self.__retrytime*random_number_between(1.0, 2))
            self.__flag.wait() # return immediately when it is True, block until the internal flag is True when it is False


    def pause(self):
        self.__flag.clear() # Set to False to block the thread


    def resume(self):
        self.__flag.set() # Set to True, let the thread stop blocking


    def stop(self):
        self.__flag.set() # Resume the thread from the suspended state, if it is already suspended
        self.__running.clear() # Set to False