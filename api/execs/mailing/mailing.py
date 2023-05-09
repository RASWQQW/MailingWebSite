import json
import sys
import asyncio
import os
import secrets
import string
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Union, Optional, Any, Iterable

import requests
import telethon
from selenium import webdriver
import telethon
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from api.forflask.base_.flask_base import Connection

from api.execs.dataclasses.dataclass import ParseResult, Attrs
import aiohttp

# from api.execs.others.test import temp_opt
from selenium.webdriver.common.by import By

from api.execs.others.test import temp_opt
from api.execs.requesting import Driver


# twilio pass: 32P/Qm&(AiZrcyTdsffds@$@#$#@


class Telegram(object):
    def __init__(self, current_path: str):
        self.current_session: Optional[telethon.TelegramClient] = None
        self.current_path= current_path

    async def Connection(self):
        from api.execs.conf.conf import Constants as ct

        session = telethon.TelegramClient(self.current_path, api_id=ct['api_id'], api_hash=ct['api_hash'])
        await session.connect()
        self.current_session = session


class TelegramMailing(Telegram):
    def __init__(self, user_session):
        super().__init__(current_path=user_session)

    async def send_message(self, number, message):
        await super().Connection()
        user_number = await self.current_session.get_entity(number)
        await self.current_session.send_message(entity=user_number, message=message)

    async def message_contact_retrieve(self):
        """"""
        pass


class TelegramGetToken(Telegram):
    """ Perform with telethon get user number send secret key and then chat
    with bot father and create bot or get exist bot token"""

    def __init__(self):
        self.current_session: Optional[telethon.TelegramClient] = None
        self.generated_user_session = f"UserSession{secrets.choice(range(999))}"
        self.current_path = f"{os.path.dirname(__file__)}\\things\\TelegramSessions\\{self.generated_user_session}"
        super().__init__(current_path=self.current_path)

    def __await__(self):
        return self.Connection().__await__()

    async def BotCreate(self, bot_name: str) -> list:
        entity = await self.current_session.get_entity('botfather')
        is_message = await self.current_session.send_message(entity=entity, message='/newbot')
        await self.current_session.send_message(entity=entity, message=bot_name)

        def bot_username_generator() -> str:
            random_word = ''
            while len(random_word) <= 4:
                random_word += secrets.choice(string.ascii_letters.split() + string.digits.split())
            return bot_name + random_word + 'bot'

        while True:
            bot_name_message = await self.current_session.send_message(entity=entity, message=bot_username_generator())
            response = await self.current_session.get_messages(entity, ids=bot_name_message.id + 1)
            if response[0].message[:5] == "Done!":
                start_index = response[0].message.find("HTTP API:") + 9
                bot_token = response[0].message[start_index: start_index+46]
                return [bot_token, self.current_path]

    async def send_code_by_number(self, phone_number: str):
        sent_request = await self.current_session.send_code_request(phone=phone_number, _retry_count=3)
        print("request sent", sent_request.phone_code_hash)
        return sent_request.phone_code_hash

    async def sign_in(self, phone_number: str, phone_hash: Optional[Any], user_code: str) -> Any:
        await self.current_session.sign_in(phone=phone_number, code=user_code, phone_code_hash=phone_hash)
        if await self.current_session.is_user_authorized():
            return True, await self.current_session.get_me()
        return False

    def clean(self):
        # the last section of process after creating a token to user
        os.remove(self.current_path)



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

        files = {'file': open("text.txt", "rb")}

        jsonLoader = {
            "chatId": number,
            "caption": caption
        }

        datas = aiohttp.FormData()
        datas.add_field(name="chatId", value=number)
        datas.add_field(name="caption", value=caption)
        datas.add_field('files', open("text.txt", "rb"), filename="testing.txt", content_type='text')

        async with aiohttp.ClientSession() as sess:
            async with sess.post(url, headers=self.headers, json=datas) as res:
                print(res.status)
                print(await res.text())

        response = requests.request('POST', url, files=files, headers=self.headers, json=jsonLoader)
        print(response.text)



class Sender(object):

    """ It is a main sender class where occurs proccesses
     that allows async task sending among other class methods"""

    def __init__(self,
                 clientText: str,
                 senderProvider: Union[TelegramMailing, Whatsapp],  # defines the sender object fo reason
                 messageType: str,
                 ListOfFirms: list[ParseResult],
                 incPhoto: bool = False,
                 incVideo: bool = False,
                 *args,
                 **kwargs
                 ):

        self.clientText=clientText
        self.sender_ins: Union[TelegramMailing, Whatsapp] = senderProvider
        self.messageType= messageType
        self.firms = ListOfFirms
        self.incPhoto = incPhoto
        self.incVideo = incVideo

        # setting kwargs params
        for key, value in kwargs.items(): setattr(self, key, value)

    async def SendMessage(self):
        for_send_tips = []; sending_loop = asyncio.get_event_loop()
        for sending_firm in self.firms:
            direct_contact = [True if soc.lower() in ['telegram', 'whatsapp'] else False for soc in sending_firm.social_medias.keys()]
            if sending_firm.phone_number or any(direct_contact):
                message = self.clientText
                for_send_tips.append(sending_loop.create_task(self.sender_ins.send_message(sending_firm, message)))



class WhatsappGetToken(object):
    """ Just creating and getting saving last user object after saving it in base_"""
    def __init__(self, driver: webdriver = None):
        self.qr_image_link: Optional[str] = None
        self.IdInstance: Union[int, str, None] = None
        self.Api_Token: Optional[str] = None
        self.driver: webdriver = driver

    async def collector(self):
        """There goes mere template of parsing and getting mere qr code and arguments of instance"""

        self.driver = webdriver.Chrome(options=temp_opt().options)

        self.check_is_login()  # get into pages
        self.create_instance()
        self.instance_manage()
        self.get_properties(current_driver=self.driver)
        result = await self.get_qr_request(api_token=self.Api_Token, id_instance=self.IdInstance)
        if result[1] == 0: self.get_qr(current_driver=self.driver)

        # second less-possible method
        # await self.get_ins_values_all()

        return self.qr_image_link, self.IdInstance, self.Api_Token


    @staticmethod
    def f_elements(parent: WebElement, val, by, id: int = None):
        fd_element = parent.find_elements(by, val); fd_element = fd_element if id is None else fd_element[id]
        print(fd_element)
        return fd_element

    @staticmethod
    def f_element(parent: WebElement, by, val, *args, **kwargs):
        return parent.find_element(by, val)

    @staticmethod
    def _val_waiter(
            parent: Union[WebElement, webdriver], params: Iterable, time_: int = 100,
            conditions: Iterable = None, loop=asyncio.get_event_loop()):

        async def timer(event_: asyncio.Event, timer_event: asyncio.Event):
            for _ in range(time_):
                if timer_event.is_set(): print("Time is out of state"); return True
                await asyncio.sleep(1)
            event_.set()

        def conditions_func(webElement):
            if conditions is None: return True
            cond_list = {"get_attr": webElement.get_attribute, }
            for cond in conditions:
                if cond['method'] == 'equal':
                    cond_result = cond_list[cond['func']](cond['attr']).lower()
                    print(cond_result)
                    if not cond_result == cond['val']:
                        return False
                if cond['method'] == 'contains':
                    if not cond_list[cond['func']](cond['attr']).lower().__contains__(cond['val']):
                        return False
            else: return True

        async def cycler(event_: asyncio.Event, t_event):
            while True:
                try:
                    if event_.is_set(): print("Waiting time is expired"); break
                    is_value = parent.find_element(*params)
                    if is_value and conditions_func(is_value):
                        print("Is outside"); t_event.set(); return is_value, True
                except Exception as e: pass

        event = asyncio.Event()
        t_event = asyncio.Event()
        def handler(future):
            print(future.result())

        gatherer = asyncio.gather(*[loop.create_task(val) for val in [timer(event, timer_event=t_event), cycler(event, t_event=t_event)]])
        gatherer.add_done_callback(handler)
        loop.run_until_complete(gatherer)

        print(gatherer.result())
        return gatherer.result()[1][0]

    def LogIn(self):
        # log in button obj
        b_xpath = "/html/body/div/div/div[1]/div[2]/div/form/div[4]/div/div/div/div/button"
        button_value = self.driver.find_element(By.XPATH, b_xpath)

        # fill reg forms
        from api.execs.conf.conf import email, password

        p_branches = self.driver.find_element(By.XPATH, '//*[@id="normal_login"]')  # ant-form ant-form-horizontal
        password_form, email_form = p_branches, p_branches


        task_list = [
            {"func": self.f_elements, "by": By.CLASS_NAME, "val": "ant-form-item", "id": {"email": 0, "pass": 1}},
            {"func": self.f_element, "by": By.CLASS_NAME, "val": "ant-input-affix-wrapper", "id": None},
            {"func": self.f_element, "by": By.ID, "val":
                {"email": "normal_login_email", "pass": "normal_login_password"}, "id": None}
        ]

        #TODO change dict to more accurate and sustainable version
        xpath_main_xpath = ""
        task_path_xpath = {
            {"xpath": "", "email": False, "pass": False}
        }

        for val in task_list:
            email_form = val['func'](email_form, by=val["by"],
                                     val=val["val"]["email"] if isinstance(val["val"], dict) else val["val"],
                                     id=val["id"]["email"] if isinstance(val["id"], dict) else val["id"])

            password_form = val['func'](parent=password_form, by=val["by"],
                                    val=val["val"]["pass"] if isinstance(val["val"], dict) else val["val"],
                                    id=val["id"]["pass"] if isinstance(val["id"], dict) else val["id"])

        password_form.send_keys(password)  # sending value of password
        email_form.send_keys(email)  # sending value of email
        self.driver.execute_script("arguments[0].click()", button_value)


    def create_instance(self):
        # wait create instance button
        c_button_class = "/html/body/div/section/section/main/div[1]/button[2]"
        plan_button_xpath = "/html/body/div/section/section/main/div/div[1]/button"

        # wait that developer plan is already arose
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, c_button_class)))

        # click create instances
        self.driver.find_element(By.XPATH, c_button_class).click()

        # select developer plan # for step in task_list2:
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, plan_button_xpath)))
        select_but_parent = self.driver.find_element(By.XPATH, plan_button_xpath)
        select_but_parent.click()

        # confirm creating the instance
        self.success_waiter()
        self.get_instance_page()

    def success_waiter(self):
        """ Wait for last success page in webdriver"""
        while True:
            # "https://console.green-api.com/instanceList/tariff/result?status=success&curTariff=DEVELOPER"
            if self.driver.current_url[-19:] == "curTariff=DEVELOPER": break

    def get_instance_page(self):
        """ By button """
        full_page_path = "/html/body/div/section/section/main"
        confirm_button = full_page_path + "/div/div[2]/button"

        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, full_page_path)))
        conf_button = self.driver.find_element(By.XPATH, confirm_button)
        conf_button.click()

    def get_instance_page_2(self):
        """ By link"""

        # 2 option is
        instance_list_link = "https://console.green-api.com/instanceList"
        self.driver.get(instance_list_link)

    def instance_manage(self):
        #  go to the instance object
        parent_xpath = "/html/body/div/section/section/main/div[2]/div/div/div/div/div/table/tbody"
        instances_class = "ant-table-row ant-table-row-level-0 InstanceListScreen_instanceRowSelected__2FzH8"
        current_url = "https://console.green-api.com/instanceList/"

        while True:
            if self.driver.current_url == current_url:
                print(self.driver.current_url); time.sleep(3); break

        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, parent_xpath)))  # ant-table-wrapper
        parent_xpath_val = self.driver.find_element(By.XPATH, parent_xpath)
        # print(is_last_val[-1].get_attribute("class"), is_last_val)
        while True:
            is_last_val = parent_xpath_val.find_elements(By.TAG_NAME, "tr")
            if is_last_val[-1].get_attribute("class").__contains__(instances_class):
                is_last_val[-1].click(); break

    async def get_ins_values_all(self):
        # getting the values of current page instance
        asyncio.get_event_loop().set_debug(enabled=True)
        get_last_r = await asyncio.get_event_loop()\
            .create_task(self.between_bridge(current_driver=self.driver, current_loop=asyncio.get_event_loop()))

        # send hole defined values after completing of tasks
        print(f"_______________The last whole result: {get_last_r}")

        self.qr_image_link, self.IdInstance, self.Api_Token = get_last_r[0], get_last_r[1][0], get_last_r[1][1]
        # send to user

    async def between_bridge(self, current_loop, current_driver):
        executor = ThreadPoolExecutor(max_workers=2)

        exec_runner = lambda func: current_loop.run_in_executor(executor, func, current_driver)
        tasks = [exec_runner(self.get_qr), exec_runner(self.get_properties)]

        results = await asyncio.gather(*tasks)
        executor.shutdown(wait=True)
        return results


    def get_qr(self, current_driver: webdriver):
        parent_xpath = '/html/body/div/section/section/main/div/div[5]'
        button_xpath = f'{parent_xpath}/div/button'
        parent_off_button = current_driver.find_element(By.XPATH, parent_xpath)  # InstanceScreen_qrContainer__2LD0S

        # tap get qr
        current_button = self._val_waiter(
            parent=current_driver, params=(By.XPATH, button_xpath),
                     conditions=[{'func': 'get_attr', 'attr': 'textContent', 'val': 'get qr', 'method': 'equal'}])
        current_button.click()

        # wait until qr code image appears
        image = self._val_waiter(parent=parent_off_button, params=(By.XPATH, f"{parent_xpath}/div/img"))
        # get qr link after appearing
        get_url = image.get_attribute("src"); self.qr_image_link = get_url
        return get_url

    def get_properties(self, current_driver: webdriver) -> tuple:
        """ get user instance values such as idiInstance and token"""

        id_instance_xpath = "/html/body/div/section/section/main/div/div[4]/div/table/tbody/"  # tr[2]/td/span/div
        desc_xpath = "/html/body/div/section/section/main/div/div[4]/div"

        desc = current_driver.find_element(By.XPATH, desc_xpath)  # ant-descriptions-view
        rows = desc.find_elements(By.TAG_NAME, "tr")[1:3]  # "ant-descriptions-row"

        # '//div[@class="InstanceScreen_minRowElem__452Lo"]'
        idInstance = rows[0].find_element(By.XPATH, f'{id_instance_xpath}tr[2]')\
            .find_element(By.XPATH, f'{id_instance_xpath}tr[2]/td/span/div').get_attribute("textContent")

        ApiToken = rows[1].find_element(By.XPATH, f'{id_instance_xpath}tr[3]')\
            .find_element(By.XPATH, f"{id_instance_xpath}tr[3]/td/span").get_attribute('textContent')

        self.IdInstance = idInstance, self.Api_Token = ApiToken
        return idInstance, ApiToken

    async def get_qr_request(self, id_instance:Union[int, str], api_token: str):
        url =f"https://api.green-api.com/waInstance{id_instance}/qr/{api_token}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url) as response:
                await response.text()
                json_result = (await response.json())
                print(json_result)
                if json_result['type'] == 'alreadyLogged': return "Instance is already authorized you can't log in ", 0
                elif json_result['type'] == 'qr':
                    self.qr_image_link = f"data:image/jpeg;base64,{json_result['qr']}"; print(self.qr_image_link)
                    return self.qr_image_link, 1
                else: return "There happened some errors", 0

    def check_is_login(self):
        self.driver.get("https://console.green-api.com/instanceList/")
        if self.driver.current_url.split('/')[-1] == "auth": self.LogIn()

    def delete_instance(self, id_instance: str):
        self.driver = webdriver.Chrome(options=temp_opt().options); self.check_is_login()
        self.driver.get(id_instance)
        self.driver.get(f"https://console.green-api.com/instanceList/{id_instance}")  # 1101813749

        del_button_xpath = '/html/body/div[1]/section/section/main/div/div[2]/div[1]/div[1]/div/div[4]/div/span'
        confirm_button_xpath = '/html/body/div[2]/div/div/div/div[2]/div/div[2]/button[2]'

        is_button = self.driver.find_element(By.XPATH, del_button_xpath)
        self.driver.execute_script("arguments[0].click();", is_button)
        conf_but_args = (By.XPATH, confirm_button_xpath)
        WebDriverWait(self.driver, 3).until(EC.presence_of_element_located(*conf_but_args))
        self.driver.find_element(*conf_but_args).click()


class WhatsappReg(object):
    def __init__(self, api_token=None, id_instance=None):
        self.id_Instance = id_instance
        self.api_token = api_token

        # notAuthorized | authorized | blocked https://green-api.com/docs/api/account/GetStateInstance/
        self.user__authorized = None
        self.recent_driver: webdriver = None
        self.connect_to_base: Any = Connection()
        self.loop__ = asyncio.new_event_loop()

    def create_instance(self):

        # there goes actually user results id instance and token and link
        # if links is not scanned and status is not authorized
        # we just save arguments and lock the mailing bool and as not authorized

        # params:: self.id_Instance. self.api_token And there last results goes to set
        # these params for next implementing

        token_get_ins = WhatsappGetToken(); self.loop__.run_until_complete(token_get_ins.collector())
        self.id_Instance, self.api_token = token_get_ins.IdInstance, token_get_ins.Api_Token

        # close the last session
        token_get_ins.driver.close()
        print(self.id_Instance, self.api_token)
        instance_id = self.connect_to_base.save_whatsapp_instance(self.id_Instance, self.api_token)

        return token_get_ins.qr_image_link, instance_id, self.id_Instance, self.api_token

    async def save_user_status(self):
        self.connect_to_base.change_whatsapp_instance_status(self.id_Instance, self.api_token, self.user__authorized)

    async def is_user_authorized(self):
        # check that the user is authorized by self
        self._check_pr()

        url = f"https://api.green-api.com/waInstance{self.id_Instance}/getStateInstance/{self.api_token}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                await resp.text()
                self.user__authorized = (await resp.json())['stateInstance']
                print(self.user__authorized)
                await self.save_user_status()

    def instance_attempt(self):
        self._check_pr()
        # by the user instance and token we go into the web and will get the qr repeatedly
        # by given values or already ready values

        instance_page = f"https://console.green-api.com/instanceList{self.id_Instance}"
        self.loop__.run_until_complete(self.is_user_authorized())
        if self.user__authorized == "authorized":
            act_driver = webdriver.Chrome(options=temp_opt().options) if not self.recent_driver else self.recent_driver
            act_driver.get(instance_page)

            WhatsappGetToken(driver=act_driver).check_is_login(); act_driver.get(instance_page)

            current_loop = asyncio.get_event_loop()
            qr_link = current_loop.run_until_complete(WhatsappGetToken().get_qr(current_driver=act_driver))

            return qr_link
        return "Account is already authorized"

    def delete_instance(self, id_instance):
        WhatsappGetToken().delete_instance(id_instance)
        self.connect_to_base.delete_user_instance(id_instance=id_instance)

    async def logout_instance(self):
        url = f"https://api.green-api.com/waInstance{self.id_Instance}/Logout/{self.api_token}"
        async with aiohttp.ClientSession() as sess:
            async with sess.get(url) as response:
                return True if (await response.json())['isLogout'] == 'true' else False

    async def wait_check_status(self):
        # lastly check that user is authorized
        for _ in range(0, 180, 30):
            await asyncio.sleep(delay=30)  # 30
            await self.is_user_authorized(); print(f"user is checked {self.user__authorized}")

    def _check_pr(self):
        for val in [self.api_token, self.id_Instance]:
            if val is None:
                raise ValueError(
                    "There must be a class values relatively by recent no too late attempt or " "by manual")


class instances(object):
    instance = 1101807124
    token = "7563794111cd4655b52e2a50a6c95c2928db0cf5e3334b8f9d"

def main():

    asyncio.run(Whatsapp(token=instances.token, idInstance=instances.instance).send_message("77789197489", "Alma"))
    # print(asyncio.run(Whatsapp(token=token, idInstance=instance).send_file("77789197489", None, "Alma")))
    # print(asyncio.run(WhatsappReg(api_token=instances.token, id_instance=instances.instance).is_user_authorized()))

async def tg_send_tester():
    instance = TelegramGetToken()
    await instance.Connection()
    res = await instance.send_code_by_number(phone_number="87789197489")
    print(res)


if __name__ == "__main__":
    # main()

    # asyncio.run(WhatsappGetToken().get_qr_request(id_instance=1101813749,
    #                                               api_token="af874c2cbb3f4d2494845201b71fcaa1e8da56ab2aaf420796"))

    # instance = WhatsappGetToken()
    # loop = asyncio.new_event_loop()
    # loop.set_debug(enabled=True)
    # final_results = loop.run_until_complete(WhatsappGetToken().whatsapp_token())
    # [print(val) for val in final_results]
    # print(f"results: {instance.IdInstance, instance.qr_image_link, instance.Api_Token}")



    # main()
    # asyncio.run(tg_send_tester())
    # asyncio.run(GetToken().telegram_token(phone_number="87789197489", code=None))
    pass