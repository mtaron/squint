import asyncio

from squint_core.hello import hello_world


async def main():
    print("Hello from ingest!")
    await hello_world()


if __name__ == "__main__":
    asyncio.run(main())
