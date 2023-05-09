import asyncio
import json
import time
from typing import Union

import aiohttp
import requests
from api.execs.dataclasses.dataclass import ParseResult


class instances(object):
    instance = 1101807124
    token = "7563794111cd4655b52e2a50a6c95c2928db0cf5e3334b8f9d"


class Whatsapp(object):
    def __init__(self, token: str, idInstance: int):
        self.token = token
        self.idInstance = idInstance
        self.firm_list: list[dict] = []
        self.inner_pr = wh_message_sender(opener=self)

    async def send_message(self, number_source: Union[ParseResult, str], message):
        if isinstance(number_source, ParseResult):
            number_source = await self.number_retriever(number_source)
        await self.inner_pr.send_text_message(number_source, message)

    async def number_retriever(self, firm_dict: ParseResult):
        """ set number as an id or get from whatsapp tag if it exists"""

        if firm_dict.social_medias["Whatsapp"]:
            special_whatsapp_number = \
                firm_dict.social_medias['Whatsapp'].splt("?phone=")[-1].split("&")[0]
            return special_whatsapp_number
        else:
            def by_numb_api():
                for number in firm_dict.phone_number:
                    response = requests.post(
                        f"https://api.green-api.com/waInstance{self.idInstance}/checkWhatsapp/{self.token}",
                        headers={"phoneNumber": number})
                    if json.loads(response.text.encode('utf-8'))['phoneNumber'] == 'true':
                        return number

            def by_request_(current_number: Union[str, int]):
                # message sending
                message_id = self.inner_pr.send_text_message(number=current_number, text="Check status")
                return self.inner_pr.delete_message(number=current_number, idMessage=str(message_id))

            # it comes to that the getting number that capable to send message by api otherwise with method
            try: by_numb_api()
            except:
                for number in firm_dict.phone_number:
                    if by_request_(number) == "in media": return number

    async def send_file(self, number, link, caption):
        await self.inner_pr.send_photo_caption_message(number, link, caption)



class wh_message_sender:
    def __init__(self, opener: Whatsapp = None, token: str = None, idInstance: int = None):
        self.token = None; self.idInstance = None
        self.headers = {'Content-Type': 'application/json'}
        self.__dict__.update(opener.__dict__)
        self.datas = {}

    # clear only text message sender
    async def send_text_message(self, number, text):
        self.datas.update({"chatId": f"{number}@c.us", "message": text})

        url = f"https://api.green-api.com/waInstance{self.idInstance}/sendMessage/{self.token}"
        async with aiohttp.ClientSession() as sess:
            async with sess.post(url, headers=self.headers, json=self.datas) as resp:
                print(resp.status)
                print(await resp.text())
                return resp.status

    def delete_message(self, number, idMessage: str):
        self.datas.update({"chatId": f"{number}@c.us", "idMessage": idMessage})
        print(self.datas)

        def deleter(is_time: int = 0):
            url = f"https://api.green-api.com/waInstance{instances.instance}/deleteMessage/{instances.token}"
            response = requests.post(url, headers=self.headers, json=self.datas)
            print(response.text, response.status_code)

            if is_time == 10:
                return "not in media"
            if response.status_code != 200:
                time.sleep(0.3); is_time+=1; deleter(is_time)
            else: return "in media"

        return deleter()


    async def send_photo_caption_message(self, number, photoLink, caption):
        url = f"https://api.green-api.com/waInstance{self.idInstance}/sendFileByUpload/{self.token}"

        files = {'file': open("../../text.txt", "rb")}

        jsonLoader = {
            "chatId": number,
            "caption": caption
        }

        datas = aiohttp.FormData()
        datas.add_field(name="chatId", value=number)
        datas.add_field(name="caption", value=caption)
        datas.add_field('files', open("../../text.txt", "rb"), filename="testing.txt", content_type='text')

        async with aiohttp.ClientSession() as sess:
            async with sess.post(url, headers=self.headers, json=datas) as res:
                print(res.status)
                print(await res.text())

        response = requests.request('POST', url, files=files, headers=self.headers, json=jsonLoader)
        print(response.text)


def main():
    asyncio.run(
        Whatsapp(token=instances.token, idInstance=instances.instance).send_message("77789197489", "Alma"))
    # print(asyncio.run(Whatsapp(token=token, idInstance=instance).send_file("77789197489", None, "Alma")))
    # print(asyncio.run(WhatsappReg(api_token=instances.token, id_instance=instances.instance).is_user_authorized()))
