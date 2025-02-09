import calendar
import datetime
import re

from bs4 import BeautifulSoup
from collections import defaultdict


async def parse_html(html: str) -> list[dict]:
    soup = BeautifulSoup(html, 'html.parser')
    user_rows = soup.select('tr[id^="bx_calendar_user_"]')
    entries = soup.select('.bx-calendar-entry')

    tops = []
    for entry in entries:
        style = entry.get('style', '')
        top = await extract_style_property(style, 'top')
        if top is not None:
            tops.append(top)

    if not tops:
        return []
    # Смотрим по порядку по top css свойству
    # Примерно каждые 25px идет следующий юзер по порядку в таблице
    # т.к div'ы с записями об отпусках идут отдельно поверх таблицы, без привязки по какому-либо id к юзеру
    sorted_tops = sorted(tops)
    initial_offset = sorted_tops[0]
    diffs = [sorted_tops[i] - sorted_tops[i - 1] for i in range(1, len(sorted_tops))]
    diff_counts = defaultdict(int)
    for d in diffs:
        diff_counts[d] += 1
    row_height = max(diff_counts, key=lambda k: diff_counts[k]) if diff_counts else 25
    if row_height <= 0:
        row_height = 25

    results = []

    for entry in entries:
        style = entry.get('style', '')
        top = await extract_style_property(style, 'top')
        left = await extract_style_property(style, 'left')

        if top is None or left is None:
            continue

        row_index = (top - initial_offset) // row_height

        if row_index < 0 or row_index >= len(user_rows):
            continue

        user_row = user_rows[row_index]
        user_link = user_row.select_one('.bx-calendar-month-first-col a')
        if not user_link:
            continue

        txt = entry.find('nobr').get_text(strip=True) if entry.find('nobr') else ''
        dates = await get_dates(txt)
        if dates[0] == '':
            continue

        results.append({
            'user_id': int(user_row.get('id', '').split('_')[-1]),
            'user_name': user_link.get_text(strip=True),
            'title': txt,
            'type': entry.get('class', ['', ''])[1].split('bx-calendar-color-')[1],
            'date_from': dates[0],
            'date_to': dates[1]
        })

    return results


async def extract_style_property(style: str, prop: str) -> int | None:
    for part in style.split(';'):
        part = part.strip()
        if part.startswith(f'{prop}:'):
            value = part.split(':')[1].strip().replace('px', '').strip()
            try:
                return int(value)
            except ValueError:
                return None
    return None


async def generate_monthly_timestamps(year: int) -> list[tuple[int, int]]:
    monthly_timestamps = []

    for month in range(1, 13):  # месяцы
        start_of_month = datetime.datetime(year, month, 1)

        last_day_of_month = calendar.monthrange(year, month)[1]
        end_of_month = datetime.datetime(year, month, last_day_of_month, 23, 59, 59)

        # б24 принимает таймштамп в милисекундах
        start_timestamp_ms = int(start_of_month.timestamp() * 1000)
        end_timestamp_ms = int(end_of_month.timestamp() * 1000)

        monthly_timestamps.append((start_timestamp_ms, end_timestamp_ms))

    return monthly_timestamps


async def get_dates(text: str) -> list[str]:
    pattern = r'\((\d{2}\.\d{2}\.\d{4})\s*-\s*(\d{2}\.\d{2}\.\d{4})\)'

    match = re.search(pattern, text)

    if match:
        first_date = match.group(1)
        second_date = match.group(2)

        return [first_date, second_date]
    return ['', '']
