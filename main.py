import json

from fastapi import FastAPI
import os
from browser import BrowserItem
from dotenv import load_dotenv
from db import DB, CalendarRepository

load_dotenv()
# asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
app = FastAPI()
browser = BrowserItem(os.getenv('BASE_BITRIX_URL'))
db = DB()
calendarRepository = CalendarRepository(db)
calendarRepository.create_table()


@app.get("/calendar/{year}")
async def root(year=2025):
    existing = calendarRepository.get_list(int(year))
    if existing is not None:
        return json.loads(existing[1])
    data = await browser.parse_bitrix_calendar(
        os.getenv('BITRIX_EMAIL'),
        os.getenv('BITRIX_PASSWORD'),
        int(year)
    )
    if data:
        calendarRepository.insert(data, int(year))

    return data
