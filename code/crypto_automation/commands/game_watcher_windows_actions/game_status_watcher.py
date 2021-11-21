import numpy as np
import time
import threading
import logging
import traceback
from win32con import *
from configparser import ConfigParser
from crypto_automation.commands.image_processing.helper import ImageHelper
from crypto_automation.commands.shared.thread_helper import Thread
from crypto_automation.commands.windows_actions.helper import WindowsActionsHelper


class GameStatusWatcherActions:
    def __init__(self, config: ConfigParser):
        self.__config = config
        self.lock = threading.Lock()
        self.__image_helper = ImageHelper()
        self.__windows_action_helper = WindowsActionsHelper(config)
        