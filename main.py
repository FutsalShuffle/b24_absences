import asyncio
from fastapi import FastAPI
import os
from browser import BrowserItem
from dotenv import load_dotenv

load_dotenv()
# asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
app = FastAPI()
browser = BrowserItem(os.getenv('BASE_BITRIX_URL'))


@app.get("/calendar/{year}")
async def root(year=2025):
    data = await browser.parse_bitrix_calendar(
        os.getenv('BITRIX_EMAIL'),
        os.getenv('BITRIX_PASSWORD'),
        int(year)
    )
    return data
