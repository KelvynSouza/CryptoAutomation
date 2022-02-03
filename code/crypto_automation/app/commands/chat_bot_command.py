import configparser
import numpy as np
import telebot
import cv2
from telebot import util
from crypto_automation.app.shared.thread_helper import Job


class ChatBotCommand:
    def __init__(self, config: configparser):
        self.__config = config
        self.__chat_id = self.__config['TELEGRAM']['chat_id']
        self.__bot = telebot.TeleBot(self.__config['TELEGRAM']['log_chat_token'])
        
    def send_log_message(self, log_message):
        if len(log_message) > 4000:
            message_to_send = util.split_string(log_message, 3000, disable_notification=True)
            for text in message_to_send:
                self.__bot.send_message(self.__chat_id, text)
        else:
            self.__bot.send_message(self.__chat_id, log_message, disable_notification=True)

    def send_log_image(self, log_image: np.array): 
        if np.any(log_image):
            image_to_send = cv2.imencode('.jpg', log_image)[1].tostring()        
            self.__bot.send_photo(self.__chat_id, image_to_send, disable_notification=True)

    def start(self):
        pooling = Job(self.__bot.infinity_polling, 0, True)
        pooling.start()
        