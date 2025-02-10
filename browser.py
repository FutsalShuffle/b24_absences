from __future__ import annotations

from asyncio import sleep
from typing import Any

import playwright.async_api
from playwright.async_api import async_playwright

import helpers


class BrowserItem:
    browser: playwright.async_api.BrowserContext | None = None
    base_url: str = ''

    def __init__(self, base_url: str):
        self.base_url = base_url

    async def get_browser(self) -> playwright.async_api.BrowserContext | None:
        if self.browser is not None:
            return self.browser
        pw = await async_playwright().start()
        browser = await pw.chromium.launch(headless=True)
        self.browser = await browser.new_context()

        return self.browser

    async def parse_bitrix_calendar(self, login: str, pwd: str, year: int) -> dict[Any, list[Any]]:
        if self.browser is None:
            await self.get_browser()
        page = await self.browser.new_page()

        await page.goto(f"{self.base_url}/stream/")
        # Логин если нужно
        if "Войти в Битрикс24" in await page.title():
            try:
                await page.locator("#login").fill(login)
                await page.locator('.b24net-login-enter-form__continue-btn').click()
            except:
                pass
            await sleep(1)
            await page.locator(".b24net-text-input__field").fill(pwd)
            await page.locator('.b24net-password-enter-form__continue-btn').click()
            await sleep(1)
        result = {}
        if f"{self.base_url}/stream/" in page.url:
            timestamps = await helpers.generate_monthly_timestamps(year)
            for i, (start_ts, end_ts) in enumerate(timestamps):
                await page.goto(self.base_url + '/timeman/#AP:month|' + str(start_ts) + '|' + str(end_ts))
                if i > 0:
                    await page.reload()
                # Ждем что таблица js загрузится
                await page.wait_for_selector(".bx-calendar-month-main-table", timeout=5000)
                try:
                    await page.wait_for_selector(".bx-calendar-entry", timeout=5000)
                except:
                    continue
                # await page.screenshot(path=str(start_ts) + ".png")
                tmp = await helpers.parse_html(await page.inner_html('body'))
                for item in tmp:
                    if item['user_id'] not in result:
                        result[item['user_id']] = []

                    if item not in result[item['user_id']]:
                        result[item['user_id']].append(item)
        await page.close()
        return result
