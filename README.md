# CryptoOcrAutomation
## Requisitos
- Portuguese(Brazil) Windows language.
- Game screen completely visible on the monitor.
- Your computer must be configured to not disable your video after some time, this can be done in energy options.
- Have your wallet already configured, using portuguese language. 
- Metamask extension icon fixed in you chrome bar and enabled to work with anonymous tab.
- Have already logged in the game at least one time.
- Your chrome MUST USE DARK THEME, this is necessary because all the templates used here were made from a dark themed chrome.

## How to install:
After clonning the repository, in *code* folder execute these cmd commands:
- Create python enviroment: python -m venv venv
- Activate enviroment: .\\venv\\Scripts\\activate
- Install this project as dependency: pip install -e .
- Install all the dependecies: pip install -r .\\crypto_automation\\requirements.txt

## How to start:
In the bat folder there is a .bat which will help to start the automation, but it is necessary to change some things within the file.
- Change the variable "venv_path" with the path for the scripts folder inside the venv folder.
- Change the variable "automation_path" with the automation path, folder where there is the file named __main__.py

## Important:
When running the automation for the first time, you'll need to configure your MetaMask wallet, follow these steps:
- On settings.ini, section "SECURITY", config "ispasswordsecured", set it to false.
- Then in section "LOGIN", config "newpassword", type your MetaMask MetaMask password.
- Change section "SECURITY", config "serviceid", to some random number of your liking
After these steps the automation will encrypt your password and use it to log in your game. 

## Telegram integration
This automation has log integration with telegram, it needs some configuration to work.
- Go to official telegram BotFather.
- Create your bot and copy bot-token (example: 000000000:dlajhslfhasoçfiopahwf ) 
- Start a conversation with the bot, so that the bot can send you messages.
- On settings.ini, section "TELEGRAM", config "log_chat_token" paste the bot-token
- Get your telegram chat_id in tha bot chat.
- Go to https://t.me/userinfobot , send "/start" and copy your telegram id
- On settings.ini, section "TELEGRAM", config "chat_id" past your telegram id