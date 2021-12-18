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
After these steps the automation will encrypt your password and use it to log in your game. 
