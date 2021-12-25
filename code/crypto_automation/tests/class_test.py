class Test:
    def __init__(self, message):
        self.__message = message
        
    def get_message(self):
        print(self.__message)

    def set_message(self, message):
        self.__message = message

mensagem = "mensagem 1"
test1 = Test(mensagem)
mensagem = "mensagem 2"
test2 = Test(mensagem)

test1.get_message()
test2.get_message()
test2.set_message("Mensagem 2 2")
test2.get_message()
test1.get_message()
