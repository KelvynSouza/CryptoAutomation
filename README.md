# CryptoOcrAutomation
Para iniciar com sucesso deve
ter o windows em portugues,
recomendado mas pode ser maior: Python 3.9.4,
Resolução do monitor ser de 1600-900 até 1920-1080
apos clonar, entre na pasta *code* e realize os comandos no cmd:
- criar ambiente python: ○ python -m venv venv
- ativar o ambiente: .\venv\Scripts\activate
- instalar projeto como pacote: pip install -e .
- intalar dependencias do projeto: pip install -r .\crypto_automation\requirements.txt

Para iniciar a automação, na pasta code realizar o comando:
python crypto_automation\___main___.py

IMPORTANTE:
Caso ao tentar clicar no "Connect Wallet" o navegador fechar, teste e ajuste a config click_y_offset,
pois provavelmente ela causa o "OutOfBounds" exception, para testar coloque o context_click() no final do comando na linha 189
actions.move_by_offset(x_body_offset, y_body_offset)*.context_click()*.perform() , isso ira basicamente simular o click direito do mousa,
ira abrir o menuzinho onde vc podera localizar a posição do mouse.
