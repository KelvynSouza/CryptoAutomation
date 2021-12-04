# CryptoOcrAutomation
## Requisitos
- Windows em portugues,
- Python 3.9.4,
- Resolução do monitor ser de ~~1600-900 até 1920-1080~~, atualmente precisa apenas ter a tela do jogo completamente visivel.

## Instruções para Instalar:
Apos clonar, entre na pasta *code* e realize os comandos no cmd:
- Criar ambiente python: python -m venv venv
- Ativar o ambiente: .\\venv\\Scripts\\activate
- Instalar projeto como pacote: pip install -e .
- Instalar dependencias do projeto: pip install -r .\\crypto_automation\\requirements.txt

## Iniciar a automação
Na pasta bat possui um .bat realiza todo o processo de inicialização, para executalo é necessario realizar algumas mudanças nele:
- Mudar a variavel "set venv_path" com o caminho dos scripts venv.
- Mudar a variavel "set automation_path" com o caminho da automação, pasta onde fica o __main__.py

## IMPORTANTE:
On settings.ini, section "COMMON", config "automation_type", there are 2 options:
- Type 1 => automation with selenium (higher probability of being caught as bot, less errors), 
- Type 2 => automation using image detection with mouse and keyboard simulation(harder to be caught as bot, more prone to get errors)

When running the automation for the first time, you'll need to configure your MetaMask wallet, follow these steps:
- On settings.ini, section "SECURITY", config "ispasswordsecured", set it to false.
- Then in section "LOGIN", config "secretphrase" and "newpassword", type your MetaMask secret phrase and MetaMask password.

#### Type 1:
Caso ao tentar clicar no "Connect Wallet" o navegador fechar, teste e ajuste a config click_y_offset,
pois provavelmente ela causa o "OutOfBounds" exception, para testar coloque o context_click() no final do comando na linha 189
actions.move_by_offset(x_body_offset, y_body_offset)*.context_click()*.perform() , isso ira basicamente simular o click direito do mousa,
ira abrir o menuzinho onde vc podera localizar a posição do mouse.


#### Type 2

Requirements:
- Your computer must be configured to not disable your video after some time, this can be done in energy options,
- Have your wallet already configured, using portuguese language, 
- Metamask extension icon fixed in you chrome bar and enabled to work with anonymous tab,
- Have already logged in the game at least one time,
- Your chrome MUST USE DARK THEME, this is necessary because all the templates used here were made from a dark themed chrome.
