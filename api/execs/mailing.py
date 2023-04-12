import asyncio
from typing import Union
from api.execs.dataclasses.dataclass import ParseResult
import aiohttp
import pywhatkit


# twillio pass: 32P/Qm&(AiZrcyTdsffds@$@#$#@

class Telegram(object):
    def __init__(self):
        pass

    def send_message(self):
        pass


class Whatsapp(object):
    def __init__(self, token: str, idInstance: int):
        self.token = token
        self.idInstance = idInstance

    async def send_message(self, number, message):
        await wh_message_sender(self.token, self.idInstance).send_text_message(number, message)

    async def send_file(self, number, link, caption):
        await wh_message_sender(self.token, self.idInstance).send_photo_caption_message(number, link, caption)

class wh_message_sender(Whatsapp):
    def __init__(self, token: str, idInstance: int):
        super().__init__(token, idInstance)

    # clear only text message sender
    async def send_text_message(self, number, text):
        headers = {'Content-Type': 'application/json'}
        datas= {
            "chatId": f"{number}@c.us",
            "message": text
        }

        url = f"https://api.green-api.com/waInstance{self.idInstance}/sendMessage/{self.token}"
        async with aiohttp.ClientSession() as sess:
            async with sess.post(url, headers=headers, json=datas) as resp:
                print(resp.status)
                print(await resp.text())

    async def send_photo_caption_message(self, number, photoLink, caption):
        url = f"https://api.green-api.com/waInstance{self.idInstance}/sendFileByUpload/{self.token}"

        jsonLoader = {
            "chatId": number,
            "caption": caption
        }

        files = [
            ('file', open("text.txt", "rb"), 'txt')
        ]

        datas = aiohttp.FormData()
        datas.add_field('files', open("text.txt", "rb"), filename="testing.txt", content_type='text')
        async with aiohttp.ClientSession() as sess:
            async with sess.post(url, json=jsonLoader, data=files) as res:
                print(res.status)



class Sender(object):

    """ It is a main sender class where occurs proccesses
     that allows async task sending among other class methods"""

    def __init__(self,
                 clientText: str,
                 senderProvider: Union[Telegram, Whatsapp],  # defines the sender object fo reason
                 messageType: str,
                 ListOfFirms: list[ParseResult],
                 incPhoto: bool = False,
                 incVideo: bool = False,
                 *args,
                 **kwargs
                 ):

        self.clientText=clientText
        self.sender_ins: Union[Telegram, Whatsapp] = senderProvider
        self.messageType= messageType
        self.firms = ListOfFirms
        self.incPhoto = incPhoto
        self.incVideo = incVideo

        # setting kwargs params
        for key, value in kwargs.items(): setattr(self, key, value)

    async def SendMessage(self):
        for_send_tips = []; sending_loop = asyncio.get_event_loop()
        for sending_firm in self.firms:
            if sending_firm.phone_number:
                current_number = sending_firm.phone_number
                message = self.clientText
                for_send_tips.append(sending_loop.create_task(self.sender_ins.send_message(current_number, message)))


def main():
    instance = 1101807124
    token = "7563794111cd4655b52e2a50a6c95c2928db0cf5e3334b8f9d"
    asyncio.run(Whatsapp(token=token, idInstance=instance).send_message("77789197489", "Alma"))
    asyncio.run(Whatsapp(token=token, idInstance=instance).send_file("77789197489", None, "Alma"))

if __name__ == "__main__":
    # main()


    import mechanize as mc
    import bs4
    from api.execs.dataclasses.dataclass import Attrs

    browser = mc.Browser()
    browser.set_handle_robots(False)
    browser.addheaders = [('User-agent', Attrs.headers['User-Agent'])]
    resp = browser.open('https://2gis.kz/almaty/search/alma/')
    # resp = browser.open('https://www.ecfrating.org.uk/v2/new/list_players.php')

    # print(bs4.BeautifulSoup(resp.get_data()).prettify())
    resps = browser.find_link(text="6", tag="a")
    req = browser.click_link(text="6", tag="a")
    # rs = browser.open(req)
    print(req)
    print(browser.geturl())
    print(bs4.BeautifulSoup(browser.response().read()).prettify())




    pass