import asyncio
import xmlrpc
import requests
from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client
from xmlrpc import(client as cl, server as server_xlm)
import telebot
from api.execs.conf.conf import Bot_Token
from api.execs.mailing import TelegramGetToken

class Token(object):
    def __init__(self):
        self.token = Bot_Token

    async def send_request_by_telethon(self):
        instance = TelegramGetToken()
        await instance

        result = await instance.send_code_by_number(phone_number="87477427022")
        print(result)

    async def send_request_by_request(self):

        headers = {
            "accept": "application/json",
            "User-Agent": "Telegram Bot SDK - (https://github.com/irazasyed/telegram-bot-sdk)",
            "content-type": "application/json"
        }

        payload = {
            "phone_number": "87789197489",
            "api_hash": "b37c46483b8f55c3a0221e9c3b859825",
            "api_id": 16147296,
            "Settings": ""
        }

        token = "2025693723:AAEVVCm7yyRXwZgr0Iw2BMPU3KLFf-JF0a0"

        link = f"https://api.telegram.org/bot{token}/sendCode/"
        response = requests.get(link, headers=headers, json=payload)
        print(response.text)


    async def with_rpc_proxy(self):
        server = SimpleXMLRPCServer(("localhost", 8000))
        print("Is runnning")

        def is_sender(n):
            return n % 2 == 0
        server.register_function(is_sender, "is_sender")
        server.serve_forever()

    async def executer(self):
        with cl.ServerProxy("http://localhost:8000") as pr:
            print(f"sended {pr.is_sender(14)}")
            print(f"sended {pr.is_sender(45)}")


if __name__ == "__main__":
    # resul = asyncio.run(Token().send_request_by_telethon())
    # result = asyncio.run(Token().send_request_by_request())
    asyncio.run(Token().with_rpc_proxy())
