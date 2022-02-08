import threading
from configparser import ConfigParser
from crypto_automation.app.commands.chat_bot_command import ChatBotCommand
from crypto_automation.app.commands.bomb_game_status_command import BombGameStatusCommand
from crypto_automation.app.commands.luna_game_status_command import LunaGameStatusCommand

class GameStarterManager:
    def __init__(self, browser: str, config: ConfigParser, password_access: str, chat_bot: ChatBotCommand , lock: threading.Lock = None):
        self.__browser = browser 
        self.__config = config  
        self.__password_access = password_access
        self.__chat_bot = chat_bot  
        self.__lock = threading.Lock() if lock == None else lock

    def start_game(self):
        if self.__browser.upper() == "MOZILLA":
            if self.__config['LUNA_CONFIG'].getboolean('enabled') == True:
                game_watcher = LunaGameStatusCommand(self.__config, self.__password_access, self.__chat_bot, self.__lock)
                game_watcher.start_game()
        else:
            game_watcher = BombGameStatusCommand(self.__config, self.__password_access, self.__chat_bot, self.__lock)
            game_watcher.start_game()

