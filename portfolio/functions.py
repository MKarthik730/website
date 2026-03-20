import asyncio
async def task1():
        print("hello")
        await asyncio.sleep(1)
        print("hai!")
async def task2():
        print("how are u")
        await  asyncio.sleep(3) 
        print("alright")
async def main():
    await asyncio.gather(task1(),task2())

asyncio.run(main())