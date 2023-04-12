import asyncio
import multiprocessing


async def executer(number):
    print(number)
    return number

def collector():
    tasks =[asyncio.create_task(executer(value)) for value in range(5)]
    return tasks

async def deriver(coroutine_tasks):
    return await asyncio.gather(*coroutine_tasks)

async def returner():
    queue = multiprocessing.Manager().dict()
    queue["tasks"] = await deriver(collector())
    return queue


async def main():
    awaiting = await returner()
    print(awaiting)

if __name__ == "__main__":
    asyncio.run(main())