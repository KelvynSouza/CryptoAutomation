# CryptoOcrAutomation
Para iniciar com sucesso deve
ter o windows em portugues,
recomendado mas pode ser maior: Python 3.9.4,
Resolução do monitor ser de 1600-900 até 1920-1080
apos clonar, entre na pasta *code* e realize os comandos no cmd:
- criar ambiente python: python -m venv venv
- ativar o ambiente: .\\venv\\Scripts\\activate
- instalar projeto como pacote: pip install -e .
- intalar dependencias do projeto: pip install -r .\\crypto_automation\\requirements.txt

Para iniciar a automação, na pasta code realizar o comando:
python crypto_automation\\____main____.py

IMPORTANTE:
Caso ao tentar clicar no "Connect Wallet" o navegador fechar, teste e ajuste a config click_y_offset,
pois provavelmente ela causa o "OutOfBounds" exception, para testar coloque o context_click() no final do comando na linha 189
actions.move_by_offset(x_body_offset, y_body_offset)*.context_click()*.perform() , isso ira basicamente simular o click direito do mousa,
ira abrir o menuzinho onde vc podera localizar a posição do mouse.

informações sobre a automação:
in settings.ini there is a place named "automation_type", there  is 2 options:
- Type 1 = automation with selenium (higher probability of being found, less errors), 
- Type 2 = automation using image detection and mouse, keyboard simulation(harder to be found, more prone to error)
when using type 2 automation, there are some requirements:
- your computer must be configured to not disable your video after a time, this can be done in energy options,
- have your wallet already configured, using portuguese language, 
- metamask extension icon fixed in you chrome bar and enabled to work with anonymous tab,
- have already logged in the game at least one time,
- and you chrome MUST USE DARK THEME, this is necessary because all the templates used here were made from a dark themed chrome.
