# test_parse.py
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s"
)

import asyncio
from db import init_db
from replay_manager import process_new_replays

async def main():
    await init_db()
    await process_new_replays()

if __name__ == "__main__":
    asyncio.run(main())
