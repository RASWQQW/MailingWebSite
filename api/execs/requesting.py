import asyncio
import json
import os
import pprint
import random
from typing import Optional, Any, Union
import aiohttp
import bs4 as bs
import requests
from attr import asdict
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from api.execs.dataclasses.dataclass import ParseResult, Attrs


class Console(object):
    @classmethod
    def show(cls, text: Any): print(text)

    @classmethod
    def skip(cls, text: Any): pass


class ParseTools:
    def __init__(self, city: str, query: str):
        self.url = f"https://2gis.kz/{city}/search/{query}"


class RequestSender(ParseTools):
    def __init__(self, query: Optional[str] = None, city: Optional[str] = None, *args, **kwargs):
        super().__init__(city, query)
        self.query = query
        self.city = city
        self.kw = kwargs

        # None objects
        self.headers = None
        self.JWGISV = None
        self.parser = None
        self.PagesInfo: Optional[list[tuple[int, str]]] = None
        self.current_path = os.path.dirname(__file__)


    def val_init_(self):
        self.JWGISV = self.GetJson()  # get all json values of parsing tags
        self.headers = Attrs.headers  # headers to set user-agent
        return self

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

    async def Sendrequest(self,
                          all_val: bool = False,
                          only_val: bool = False,
                          rev_as: bool = False,
                          rev_as_val: tuple = None,
                          link: str = None) -> Union[list, dict, Any]:

        async with aiohttp.ClientSession() as session:
            async def SearchContentParser() -> BeautifulSoup:
                async with session.get(self.url, headers=Attrs.headers) as response:
                    assert response.status == 200
                    text = await response.text()
                    self.parser = bs.BeautifulSoup(markup=text, features="lxml")
                    return self.parser


            async def GettingFullPages() -> list:
                if self.PagesInfo is None:
                    self.PagesInfo = await FrDriver().GettingPages(self.url)
                return self.PagesInfo

            async def GetCount() -> int:
                return len(self.PagesInfo)

            async def GetAllPages() -> int:
                self.val_init_()
                currentClue = self.parser
                for name in self.JWGISV["GetAllPagesCount"]:
                    currentClue = currentClue.find(name=name["name"], class_=name["cl"])

                # print("LastElem", pprint.pprint(str(currentClue.findChildren)))
                elements = currentClue.find_all(name="a", class_="_12164l30")
                pages = len(elements) + 1; print("Page amount: ", pages)
                return pages

            async def GetFullList():
                """ You will get all list of accordingly to request"""

                # # to get self.parser to get access for link page straightly
                # await SearchContentParser()
                # to get all pages parsing via webdriver
                await GettingFullPages()

                waiters = [GetCount(), Parser().GetAllContents()]; waited = []
                for task in waiters: waited.append(asyncio.create_task(task))

                resultsFromTasks = await asyncio.gather(*waited)
                # print(type(resultsFromTasks[0]), type(resultsFromTasks[1]))
                self.WriteJson(values=resultsFromTasks[1])
                return resultsFromTasks

            async def GetFirm():
                """ You will get only one firm"""
                # set link
                return await Parser().ParseFirm() if link is None else Parser().ParseFirm(firm_link=link)

            async def getFullAsync() -> asyncio:
                return await Parser().GetAllContents(on_page=(True, rev_as_val))

            if all_val: return await GetFullList()
            elif only_val: return await GetFirm()
            elif rev_as: return await getFullAsync()
            else: raise ValueError("You must to give some params")


class Parser(object):
    def __init__(self):
        self.JWGISV = RequestSender().val_init_().JWGISV

        # for setting pages
        self.PagesInfo = None

    async def SetPages(self, pages: list[tuple[int, str]]):
        self.PagesInfo = pages

    async def ParseFirm(self, firm_link: str = "/almaty/firm/9429940000962391") -> ParseResult:
        firm_link = f"https://2gis.kz{firm_link}"
        menu = "tab/menu"
        menu = "tab/reviews"
        menu = "tab/info"

        async with aiohttp.ClientSession() as session:
            async with session.get(url=firm_link, headers=Attrs.headers) as resp:
                ContentText: str = await resp.text()

        IndParser = bs.BeautifulSoup(ContentText, features='lxml')
        main_block = IndParser.find(name="div", class_="_18lzknl")
        review_block = main_block.find(name="div", class_="_1tfwnxl")
        add_block = main_block.find(name="div", class_="_1b96w9b")
        add_block_under = add_block.find(name="div", class_="_t0tx82")
        ...

        # clearly zone starts
        @RequestSender.Exceptionoid
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

            return {"name": cmp_name, "occupancy": occp, "rating": float(rating) if rating else None,
                    "about": cmp_about}

        ...

        @RequestSender.Exceptionoid
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

        @RequestSender.Exceptionoid
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

        @RequestSender.Exceptionoid
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

        @RequestSender.Exceptionoid
        async def GetWebPage(console: Console = None) -> dict:
            get_content_webpage = add_block_under.find_all("div", class_="_49kxlr")[1];
            page_link = None
            if get_content_webpage: page_link = get_content_webpage.findNext("a", class_="_1rehek").get("href")
            return {"website": page_link}

        @RequestSender.Exceptionoid
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
        for task in tasks: ReadyTasks.append(newTask.create_task(
            RequestSender().Deleter(await task), name=str(task.__name__)))

        Stuffs = await asyncio.gather(*ReadyTasks)
        newStuffs = {"firm_id": firm_link}  # to set the firm_link for advance

        # to check full stuff definition for accept them in loop
        if Stuffs is not None:
            for stuff in Stuffs:
                # check that the newStuffs is not capable dict as much as not seems
                try:
                    newStuffs.update(stuff)
                except Exception as e:
                    pass  # print("EXXX", e)

        # changing_tasks = []
        # for key, value in newStuffs.items():
        #     changing_tasks.append(asyncio.create_task(self.Deleter(key)))
        # # print("newStuffResult", newStuffs)
        # changing_results = await asyncio.gather(*changing_tasks)

        return ParseResult(**newStuffs)

    async def GetAllContents(self, pages=False, on_page: tuple[bool, tuple[int, str]] = (False, ())) -> Any:
        AllTasks = []

        print("______Task Start page:", on_page[1][0])
        # It works as done callback but little different as async and returns getSteep()
        async def SteepGetting(resultobj: ParseResult):
            return resultobj.getSteep()
        # This method receives coroutine and then await it then returns await result from above back
        async def asyncRegulator(coroutine):
            return await SteepGetting(await coroutine)

        def PageEditor(in_page: tuple[int, str]):
            parser = bs.BeautifulSoup(markup=in_page[1], features='lxml')
            content = parser\
                .find_all(name=self.JWGISV["GetACC"]["step1"]["name"], class_=self.JWGISV["GetACC"]["step1"]["cl"])[-1]

            # print("ContentsFull", len(content.find_all(name="div", class_="_aa8wln")))

            # get current page firms and then further occurs retrieving a link in the loop
            contents = content\
                .find_all(name=self.JWGISV["GetACC"]["step2"]["name"], class_=self.JWGISV["GetACC"]["step2"]["cl"])

            for content in range(len(contents)):
                linkIs = contents[content]\
                    .find(name=self.JWGISV["GetACC"]["step5"]["name"], class_=self.JWGISV["GetACC"]["step5"]["cl"])
                FirmLink = linkIs.get("href")

                AllTasks.append(asyncRegulator(
                    asyncio.create_task(self.ParseFirm(firm_link=FirmLink))))

        if pages:
            # pages = await GetAllPages()
            realPages: list[tuple[int, str]] = self.PagesInfo
            print("realPages", len(realPages))

            for page in range(len(realPages)):
                PageEditor(realPages[page])
        elif on_page[0]:
            PageEditor(on_page[1])

        ListOfLinks: list[Any] = await asyncio.gather(*AllTasks)
        # ListOfLinks = [objectValue.getSteep() for objectValue in ListOfLinks]
        return list(ListOfLinks)


class optbuild:
    def __init__(self, GivenOption: webdriver):
        self.opt: webdriver = GivenOption()

    def add_arg(self, arg: str):
        self.opt.add_argument(arg)
        return self

    def build_opt(self) -> webdriver:
        self.opt.add_experimental_option("detach", True)
        return self.opt

class FrDriver(object):
    def __init__(self, setopt: webdriver = webdriver.ChromeOptions):
        self.options: webdriver = optbuild(GivenOption=setopt)\
            .add_arg(f"user-agent={Attrs.headers}")\
            .add_arg("--disable-blink-features=AutomationControlled")\
            .build_opt()
        # .add_arg(f"--proxy-server={'.'.join(str([random.randint(0, 255) for _ in range(4)]))}:4556")\

    async def GettingPages(self, url) -> Any:

        session = webdriver.Chrome(options=self.options)
        session.get(url)

        # basic class of number page
        basicClass = "_1x4k6z7"

        ListPages: list[Union[asyncio.Future, asyncio.Task]] = []
        def Cercluar(object: webdriver.remote, page_number: int, buttonxpath: str = None):

            # check that in page locates all attributes for parsing
            while True:
                parent_class = session.find_elements(By.CLASS_NAME, "_awwm2v")
                if len(parent_class) >= 2:
                    # it is a optional but quite severe checking
                    firms = parent_class[1].find_elements(By.CLASS_NAME, "_aa8wln")
                    if len(firms) > 0:
                        htmlis = session.page_source
                        print(htmlis[:20] + "...")
                        break

            task = Parser().GetAllContents(on_page=(True, (page_number, htmlis)))
            print(task)

            async def wrapper_waiter():
                return await asyncio.create_task(task)
            ListPages.append(asyncio.create_task(wrapper_waiter()))

            # the last crucial action is open a next page
            # execute click script to pass next page
            session.execute_script("arguments[0].click();", object)

        while True:
            # get obvious parent class of page numbers
            parentClass = session.find_element(By.CLASS_NAME, basicClass)
            # get all links where stands links or buttons from parent class
            numberLinks: list[Any] = parentClass.find_elements(By.TAG_NAME, "a")
            # get current page number by class
            unclikable: int = int(parentClass
                                  .find_element(By.CLASS_NAME, "_l934xo5")
                                  .find_element(By.CLASS_NAME, "_19xy60y").get_attribute("innerHTML"))

            def get_inner_object_of_next_number():
                for value in numberLinks:
                    # isinner = value.find_element(By.TAG_NAME, "span")
                    # print(isinner, isinner.get_attribute("class"), value.get_attribute("href"))

                    try: valueNumber = int(value.find_element(By.CLASS_NAME, "_19xy60y").get_attribute("innerHTML"))
                    except Exception as e:
                        valueNumber = value.get_attribute("href").split("/")[-1]
                        valueNumber = int(valueNumber) if valueNumber.isdigit() else 1

                    if valueNumber == unclikable + 1:
                        is_value = value; page_number = unclikable + 1
                        return is_value, page_number

                # if there is no number greater than current page it just goes to stop
                else: return False

            result = get_inner_object_of_next_number()
            if result is not False:
                # print(result[0])
                Cercluar(object=result[0], page_number=result[1])
            else: break

        # finally it (session) goes to close
        session.close()
        full_file_results = asyncio.gather(*ListPages)
        await full_file_results
        return full_file_results.result()


if __name__ == "__main__":
    # res = asyncio.run(FrDriver().GettingPages("https://2gis.kz/almaty/search/бургер"))

    # result = asyncio.run(RequestSender(query="самса", city="almaty").Sendrequest(all_val=True))
    result = asyncio.run(FrDriver().GettingPages(url="https://2gis.kz/almaty/search/самса"))
    pprint.pprint(result, width=65, indent=1, compact=True)
    RequestSender().WriteJson(result)
    print("Total firm amount: ", len(result))
    # res = asyncio.run(RequestSender(query="alma", city="almaty").Sendrequest())

