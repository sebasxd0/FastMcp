import asyncio
from pathlib import Path

from fastmcp import Client

client = Client(Path("main.py"))


async def main():
    async with client:
        result = await client.call_tool("greet", {"name": "World"})
        print(result)


if __name__ == "__main__":
    asyncio.run(main())
