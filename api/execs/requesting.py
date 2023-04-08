import asyncio
import json
import os
import pprint
from typing import Optional, Any, Union
import aiohttp
import bs4 as bs
import requests
from attr import asdict
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By

from api.execs.dataclasses.dataclass import ParseResult, Attrs


class Console(object):
    @classmethod
    def show(cls, text: Any): print(text)

    @classmethod
    def skip(cls, text: Any): pass


class RequestSender(object):
    def __init__(self, query: Optional[str] = None, city: Optional[str] = None, *args, **kwargs):
        self.query = query
        self.city = city
        self.kw = kwargs

        # None objects
        self.parser = None
        self.current_path = os.path.dirname(__file__)

    # for delete prefixes inside string
    def delFor(self, stringValue):
        prefixes = ['\u200b', '\xa0']
        for pref_val in prefixes: stringValue = stringValue.replace(pref_val, "")
        return stringValue

    async def Deleter(self, value: Union[str, list, dict]):
        if isinstance(value, str): return self.delFor(value)
        elif isinstance(value, list):
            for val in enumerate(value):
                if isinstance(val[1], str): value[val[0]] = self.delFor(val[1])
                else: pass
            return value
        elif isinstance(value, dict):
            def DeleterRec(InnerValue: dict):
                for items, valin in InnerValue.items():
                    if type(valin) == str: InnerValue[items] = self.delFor(valin)
                    elif type(valin) == dict: DeleterRec(valin)
                    elif type(valin) == list:
                        for elem in enumerate(valin): InnerValue[items][valin[elem[0]]] = self.delFor([elem[1]])
                return InnerValue
            return DeleterRec(value)
        else: return value

    async def JsonDel(self, ParsValue: str):
        cleanValue = self.delFor(str(ParsValue))
        return json.loads(cleanValue)

    def GetJson(self):
        with open(f"{self.current_path}/things/tagst.json", "r") as values:
            value = json.load(values)
        return value

    def WriteJson(self, values: dict):
        with open(f"{self.current_path}/things/forcheck.json", "w") as val:
            json.dump(values, val, indent=5, separators=(', ', ': '))

    @staticmethod
    def Exceptionoid(func):
        async def wrapper(*args, **kwargs):
            try:
                # print("Runned: ", func.__name__, id(func))
                # here located simple object to show or skip of console
                return await func(Console().skip)
            except AssertionError as assertis:
                print(assertis, "fully no have idea")
            except Exception as e:
                print(f"Exx while parsing: {repr(e)}")

        return wrapper

    async def Sendrequest(self, all_val: bool = None,  only_val: bool = None, link: str = None) -> Union[list, dict, Any]:

        url = f"https://2gis.kz/{self.city}/search/{self.query}"

        async with aiohttp.ClientSession() as session:
            JWGISV = self.GetJson()  # get all json values of parsing tags
            headers = Attrs.headers  # headers to set user-agent

            async def SearchContentParser() -> BeautifulSoup:
                async with session.get(url, headers=Attrs.headers) as response:
                    assert response.status == 200
                    text = await response.text()
                    self.parser = bs.BeautifulSoup(markup=text, features="lxml")
                    return self.parser

            async def ParseFirm(firm_link: str = "/almaty/firm/9429940000962391") -> ParseResult:
                firm_link = f"https://2gis.kz{firm_link}"
                menu = "tab/menu"
                menu = "tab/reviews"
                menu = "tab/info"

                async with session.get(url=firm_link, headers=headers) as resp:
                    ContentText: str = await resp.text()

                IndParser = bs.BeautifulSoup(ContentText, features='lxml')
                main_block = IndParser.find(name="div", class_="_18lzknl")
                review_block = main_block.find(name="div", class_="_1tfwnxl")
                add_block = main_block.find(name="div", class_="_1b96w9b")
                add_block_under = add_block.find(name="div", class_="_t0tx82")
                # print(main_block is not None, review_block is not None,
                #       add_block is not None, add_block_under is not None)
                ...

                # clearly zone starts
                @self.Exceptionoid
                async def GetMainContent(console: Console = None) -> dict:
                    cmp_name = review_block.find(name="h1", class_="_tvxwjf").text
                    cmp_about = None
                    # is that this section check that the firm is elite whether not and if so gets block about rt
                    if len(review_block.find_all("span", class_="_3739c8")) > 1:
                        cmp_about1 = review_block.find("div", class_="_xcqknf").find("div", class_="_snijgp")
                        if cmp_about1: cmp_about = cmp_about1.text
                    else:
                        tags = [["div", "_1idnaau"], ["span", "_1w9o2igt"]]; rp = review_block
                        for elems in tags:
                            caught_from = rp.find(name=elems[0], class_=elems[1])
                            if caught_from is not None: rp = caught_from
                            else: break
                        cmp_about = rp.text

                    cmp_ocp = review_block.find("div", class_="_1idnaau")
                    occp = cmp_ocp.find("span", class_="_1w9o2igt").text if cmp_ocp else None

                    rate = review_block.find("div", class_="_146hbp5")
                    rating = rate.find("div", class_="_y10azs").text if rate else None

                    return {"name": cmp_name, "occupancy": occp, "rating": float(rating) if rating else None, "about": cmp_about}
                ...
                @self.Exceptionoid
                async def GetAddress(console: Console = None) -> dict:
                    get_address_step1 = add_block_under.find("div", class_="_13eh3hvq")
                    get_streets = get_address_step1.find("span", class_="_14quei").find("a", class_="_2lcm958")
                    get_street = {"text": get_streets.text, "link": get_streets.get("href")}

                    get_floor = get_address_step1.find("span", class_="_14quei").find_all("span", class_="_er2xx9")
                    get_floor = get_floor[1].text if len(get_floor) >= 2 else None

                    get_extend_scale_location = get_address_step1.find("div", class_="_1p8iqzw").text
                    address = dict(street=get_street, floor=get_floor, city=get_extend_scale_location)
                    return {"address": address}
                # clearly zone ends
                ...
                @self.Exceptionoid
                async def GetPhoneNumber(console: Console = None) -> dict:
                    get_cmp_phone_number = add_block_under.find_all(name="div", class_="_49kxlr")
                    phone_number = None
                    console(text=("Phone", len(get_cmp_phone_number), get_cmp_phone_number))
                    if len(get_cmp_phone_number) >= 3:
                        get_cmp_phone_number = get_cmp_phone_number[2]
                        if get_cmp_phone_number:
                            value = get_cmp_phone_number.find("a", class_="_2lcm958")
                            if value:
                                phone_number = value.get("href")
                        return {"phone_number": phone_number}

                @self.Exceptionoid
                async def GetSocialMedias(console: Console = None) -> dict:
                    get_social_cont = add_block_under.find("div", class_="_1ctt2iz")
                    social_medias = {}
                    if get_social_cont:
                        get_social_cont = get_social_cont.find_all("div", class_="_14uxmys")
                        for contacts in get_social_cont:
                            contact = contacts.find(name="a", class_="_1rehek")
                            if contact is not None:
                                link = contact.get("href"); name = contact.get("aria-label"); social_medias[name] = link
                    return {"social_medias": social_medias}

                @self.Exceptionoid
                async def GetWebPage(console: Console = None) -> dict:
                    get_content_webpage = add_block_under.find_all("div", class_="_49kxlr")[1]; page_link = None
                    if get_content_webpage: page_link = get_content_webpage.findNext("a", class_="_1rehek").get("href")
                    return {"website": page_link}

                @self.Exceptionoid
                async def GetMail(console: Console = None) -> dict:
                    get_content_mail = add_block_under.find_all("div", class_="_172gbf8")
                    # print(len(get_content_mail), get_content_mail)
                    mail_link = None
                    if len(get_content_mail) >= 4:
                        get_content_mail = get_content_mail[3]
                        if get_content_mail:
                            inner_content = get_content_mail.find("div", class_="_49kxlr")
                            console(text=(inner_content.find("a")))

                            if inner_content:
                                m1 = inner_content.find("a", class_="_1rehek", target="_blank")
                                if m1: mail_link = m1.text
                                m2 = inner_content.find("a", class_="_2lcm958", target="_blank")
                                if m2: mail_link = m2.text
                    return {"mail": mail_link}

                tasks = [GetMainContent(), GetMail(),
                         GetAddress(), GetWebPage(), GetSocialMedias(), GetPhoneNumber()]

                newTask = asyncio.get_event_loop(); ReadyTasks = []
                for task in tasks: ReadyTasks.append(newTask.create_task(self.Deleter(await task), name=str(task.__name__)))
                Stuffs = await asyncio.gather(*ReadyTasks)
                newStuffs = {"firm_id": firm_link}  # to set the firm_link for advance

                # to check full stuff definition for accept them in loop
                if Stuffs is not None:
                    for stuff in Stuffs:
                        # check that the newStuffs is not capable dict as much as not seems
                        try: newStuffs.update(stuff)
                        except Exception as e: pass  # print("EXXX", e)

                # changing_tasks = []
                # for key, value in newStuffs.items():
                #     changing_tasks.append(asyncio.create_task(self.Deleter(key)))
                # # print("newStuffResult", newStuffs)
                # changing_results = await asyncio.gather(*changing_tasks)

                return ParseResult(**newStuffs)

            async def GetCount() -> tuple[str, int]:
                currentClue = self.parser
                for step in JWGISV["GettingNumberOfResults"]:
                    currentClue = currentClue.find(name=step["name"], class_=step["cl"])

                pages = int(currentClue.text) // 12
                return currentClue.text, pages

            async def GetAllPages() -> int:
                currentClue = self.parser
                for name in JWGISV["GetAllPagesCount"]:
                    currentClue = currentClue.find(name=name["name"], class_=name["cl"])

                print("LastElem", pprint.pprint(str(currentClue.findChildren)))
                elements = currentClue.find_all(name="a", class_="_12164l30")
                pages = len(elements) + 1; print(pages)
                return pages

            async def GetAllContents() -> Any:
                pages = await GetAllPages()
                AllTasks = []
                for page in range(pages):

                    async with session.get(url=f"{url}/page/{page}", headers=headers) as res:
                        TextIs = await res.text()

                    parser = bs.BeautifulSoup(markup=TextIs, features='lxml')
                    content = parser.find_all(name=JWGISV["GetACC"]["step1"]["name"], class_=JWGISV["GetACC"]["step1"]["cl"])[-1]
                    # get current page firms and then further occurs retrieving a link in the loop
                    contents = content.find_all(name=JWGISV["GetACC"]["step2"]["name"], class_=JWGISV["GetACC"]["step2"]["cl"])

                    for content in range(len(contents)):
                        linkIs = contents[content].find(name=JWGISV["GetACC"]["step5"]["name"], class_=JWGISV["GetACC"]["step5"]["cl"])
                        FirmLink = linkIs.get("href")
                        AllTasks.append(asyncio.create_task(ParseFirm(firm_link=FirmLink)))

                def SteepGetting(future):
                    future.result()

                gathering = asyncio.gather(*AllTasks); gathering.add_done_callback(SteepGetting)
                ListOfLinks: list[ParseResult] = await gathering
                # ListOfLinks = [objectValue.getSteep() for objectValue in ListOfLinks]
                return list(ListOfLinks)


            async def GetFullList():
                """ You will get all list of accordingly to request"""

                # to get self.parser to get access for link page straightly
                await SearchContentParser()

                waiters = [GetCount(), GetAllContents()]; waited = []
                for task in waiters: waited.append(asyncio.create_task(task))

                resultsFromTasks = await asyncio.gather(*waited)
                # print(type(resultsFromTasks[0]), type(resultsFromTasks[1]))
                # self.WriteJson(values=resultsFromTasks[1])
                return resultsFromTasks

            async def GetFirm():
                """ You will get only one firm"""
                # set link
                return await ParseFirm() if link is None else ParseFirm(firm_link=link)

            if all_val: return await GetFullList()
            elif only_val: return await GetFirm()
            else: raise ValueError("You must to give some params")


class TextCleaner(object):
    def __init__(self):
        pass

    def Cleaner(self):
        pass


if __name__ == "__main__":
    result = asyncio.run(RequestSender(query="самса", city="almaty").Sendrequest(all_val=True))
    pprint.pprint(result[1], width=65, indent=1, compact=True)
    print(len(result[1]))
    # res = asyncio.run(RequestSender(query="alma", city="almaty").Sendrequest())
