# from api.execs.requesting import RequestSender as rr
import asyncio
import copy
import time
from typing import Optional, Union

from selenium.webdriver import Keys
from api.execs.requesting import FrDriver
import selenium.webdriver as dr
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.remote.webelement import WebElement
import multiprocessing as mc


async def Waiting(webdriver):
    while True:
        value = webdriver.find_element(By.TAG_NAME, "script")
        if value: break


class MainProcess(object):
    def __init__(self, query: str = None, city: str = None):
        """ Getting the ready clycle that for getting base process"""

        self.query = query
        self.city = city
        self.task_values: Union[list[mc.Manager, list[mc.Process],list[ mc.Manager], mc.Event,  list[mc.Event]], None] = None
        self.url = f"https://2gis.kz/{self.city}/search/{self.query}"

        pass

    def run_tasks(self):
        if hasattr(self, "task_values") and self.task_values is not None: return self.task_values
        self.task_values = self.Allocator(); return self.task_values

    def run__search_task(self):
        loop = asyncio.new_event_loop()
        pages, firms, get_task_count = loop.run_until_complete(ParserPart().CountGetter(self.url))

        t_c_raising = 0
        for dict_manager in self.task_values[2]:
            dict_manager["task_values"] = {"query": self.url, "during": (t_c_raising, t_c_raising + get_task_count)}
            t_c_raising += get_task_count

        # print("At the end", url, get_task_count, self.task_values[2], self.task_values[3].is_set())
        self.task_values[3].set()

        # for process in get_result[1]: process.join(
        for inner_waiting_events in self.task_values[4]:
            inner_waiting_events.wait(); inner_waiting_events.clear()

        for values in self.task_values[0].values():
            print(values); values.clear()


    def Allocator(self):
        # getting pages count
        # loop = asyncio.new_event_loop()
        # pages, firms, task_count = loop.run_until_complete(CountGetter())
        common_event = mc.Event()
        process_lists, queue_lists, inner_events = [], [], []
        valueDict = mc.Manager().dict()
        for val in range(3):
            new_val_queue = mc.Manager().dict()
            inner_event = mc.Event()
            kwargs = dict(
                driver={"driver": dr.Chrome, "opt": FrDriver}, result_collector=valueDict, task_name=f"Task {val}",
                page_event=common_event, query_value=new_val_queue, executing_waiter=inner_event)
            pr = mc.Process(target=Event_Waiting().ProcessOpener, kwargs=kwargs)

            process_lists.append(pr)
            queue_lists.append(new_val_queue)
            inner_events.append(inner_event)

            pr.start()
        return [valueDict, process_lists, queue_lists, common_event, inner_events]


class ParserPart(object):
    def __init__(self):
        pass

    async def CountGetter(self, url: str = None) -> tuple[int, int, int]:
        checking_driver = dr.Chrome(options=FrDriver().options)
        checking_driver.get(url)

        for tag in ["_166m4gk", "_nude0k3", "_rdxuhv3", "_1xhlznaa"]:
            attr = checking_driver.find_element(By.CLASS_NAME, tag)

        firm_count = attr.get_attribute("innerHTML");
        firm_count = int(firm_count)
        page_count = firm_count // 12 if firm_count % 12 == 0 else firm_count // 12 + 1
        task_ratio_count = page_count // 3 if page_count % 3 == 0 else page_count // 3 + 1

        checking_driver.close()

        return page_count, firm_count, task_ratio_count


    def dr_cycle(self, driver: Union[dr.Chrome, dr.Firefox],
                 given_link: str,
                 executing_waiter: mc.Event,
                 result_collect: mc.Manager = None,
                 task_name: str = None,
                 firm_count: tuple[int, int] = None):
        print(f"task_name is: {task_name}, pages {firm_count}")
        driver.get(given_link)
        # await Waiting(driver)

        if firm_count:
            async_result = {"queues": f"{given_link} count {firm_count}",
                            "awaitable_task": asyncio.run(self.GettingSource(driver, task_name, during=firm_count))}
            print(async_result)
            result_collect[f"{task_name}_result"] = async_result
            # at the end after inserting values for each dicts invokes wait breaker
            executing_waiter.set()
            print("Inner event Value was set")
            # return list_of_parsing_cour
        # return driver


    def parent_get(self, dr: dr) -> WebElement:
        parent = dr.find_element(By.CLASS_NAME, "_1x4k6z7")
        return parent


    async def CheckItPresence(self, driver: dr):
        while True:
            parent_class = driver.find_elements(By.CLASS_NAME, "_awwm2v")
            if parent_class and len(parent_class) > 1:
                break


    async def GettingSource(self, dr: dr, current_task_name, during: tuple[int, int]):
        parent = self.parent_get(dr)
        list_of_page_parsing_async = []
        # print(dr, during)
        while True:
            # finding all links from beneath
            keys = parent.find_elements(By.CLASS_NAME, "_12164l30")
            # finding a current page number
            current = parent.find_element(By.CLASS_NAME, "_l934xo5") \
                .find_element(By.CLASS_NAME, "_19xy60y").get_attribute("innerHTML")

            # check that must last iterate number is less than during
            if int(current) < during[1]:
                # for save current pages as process to took it result by gather
                if during[0] <= int(current):
                    # wait until ending full loading a pge
                    await Waiting(dr)
                    await self.CheckItPresence(dr)
                    # and then goes self custom waiting coroutines

                    list_of_page_parsing_async.append(asyncio.create_task(
                        self.ParsingProcess(dr.page_source, c_t=current_task_name)))

                # only controlling of next page passing way
                for val in keys:
                    getting_number = val.get_attribute("href").split("/")[-1]
                    getting_number = int(getting_number) if getting_number.isdigit() else 1
                    # print(getting_number, current)
                    if getting_number == int(current) + 1:
                        dr.execute_script("arguments[0].click();", val); break
                else: break
            else: break
        return await asyncio.gather(*list_of_page_parsing_async)

    async def ParsingProcess(self, html_text: str, **kwargs):
        """ Parsing process part of cycle
        To Create More relative connection
        """
        if "c_t" in kwargs: print("Task Name Is: ", kwargs.get("c_t"))
        return html_text[:40] + "..."




class Event_Waiting(object):
    def __init__(self):
        pass

    def ProcessOpener(self,
                    driver: Union[dict, dr],
                    task_name: str,
                    query_value: mc.Manager,
                    result_collector: mc.Manager,
                    page_event: mc.Event,
                    executing_waiter: mc.Event,
                    link: Union[str, None, ...] = "https://2gis.kz/almaty/search/alma"):

        if isinstance(driver, dict):
            print(f"Connected: {task_name}, dr id: {id(driver), driver}")

            new_driver = driver["driver"](options=driver["opt"]().options)
            new_driver.get(link)

            while True:
                waiting_results = self.EventWaiter(wait_event=page_event, sending_value_dicts=query_value)
                # print("values", waiting_results[0], waiting_results[1])

                ParserPart().dr_cycle(driver=new_driver,
                         given_link=waiting_results[0],
                         firm_count=waiting_results[1],
                         task_name=task_name,
                         result_collect=result_collector,
                         executing_waiter=executing_waiter)
                print("dr_cycle runned")


    def EventWaiter(self, wait_event: mc.Event, sending_value_dicts: mc.Manager) -> list[str, tuple[int, int]]:
        # print("We above wait")
        wait_event.wait()
        # there must occur thing that gives as number of pages and query message
        gathered_values_from_queue = sending_value_dicts.values()[0]

        # clearing a event and manager to the next tasks
        sending_value_dicts.clear()
        wait_event.clear()

        # print(gathered_values_from_queue, type(gathered_values_from_queue))
        query_message = gathered_values_from_queue["query"]
        firm_page_count = gathered_values_from_queue["during"]
        return [query_message, firm_page_count]




# This class kind of testing instance of main Process
def total_runner(get_result: list[mc.Manager, mc.Process, list[mc.Manager], mc.Event, list[mc.Event]]):
    print(get_result)
    while True:
        value = input("write word")
        url = f"https://2gis.kz/almaty/search/{value}"
        loop = asyncio.new_event_loop()
        pages, firms, get_task_count = loop.run_until_complete(ParserPart().CountGetter(url))

        t_c_raising = 0
        for dict_manager in get_result[2]:
            dict_manager["task_values"] = {"query": url, "during": (t_c_raising, t_c_raising + get_task_count)}
            t_c_raising += get_task_count

        print("At the end", url, get_task_count, get_result[2], get_result[3].is_set())
        get_result[3].set()

        # for process in get_result[1]: process.join(
        print("While is waiting now")
        for inner_waiting_events in get_result[4]:
            inner_waiting_events.wait()
            inner_waiting_events.clear()

        print("While waiting ended")

        for values in get_result[0].values():
            print(values); values.clear()


if __name__ == "__main__":
    all_values_of_process = MainProcess().Allocator()
    total_runner(all_values_of_process)


# webdriver.switch_to.new_window()
# windows = webdriver.window_handles; print(windows)
# webdriver.switch_to.window(windows[0])
