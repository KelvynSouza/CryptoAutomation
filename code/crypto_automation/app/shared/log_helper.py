import logging
from crypto_automation.app.commands.chat_bot_command import ChatBotCommand
from crypto_automation.app.shared.windows_action_helper import WindowsActionsHelper


def error(message, chat_bot: ChatBotCommand = None):
    logging.error(message)
    if chat_bot:
        try:
            chat_bot.send_log_message(message)
        except:
            pass  


def warning(message, chat_bot: ChatBotCommand = None):
    logging.warning(message)
    if chat_bot:
        try:
            chat_bot.send_log_message(message)  
        except:
            pass 


def image(windows_actions: WindowsActionsHelper, chat_bot: ChatBotCommand = None):
    windows_actions.save_screenshot_log()
    if chat_bot:
        try:
            image_to_send = windows_actions.take_screenshot()
            chat_bot.send_log_image(image_to_send) 
        except:
            pass 
        

