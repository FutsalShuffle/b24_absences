import json
import sqlite3
from datetime import datetime, timedelta
from typing import Any


class DB:
    def __init__(self):
        self.connection = sqlite3.connect('db.db')
        self.cursor = self.connection.cursor()


class CalendarRepository:
    def __init__(self, db: DB):
        self.db = db

    def create_table(self):
        self.db.cursor.execute('''
        CREATE TABLE IF NOT EXISTS calendars (
        id INTEGER PRIMARY KEY,
        data TEXT NOT NULL,
        year INTEGER NOT NULL,
        created_at INTEGER NOT NULL
        )
        ''')

    def insert(self, data: dict[Any, list], year: int):
        current_datetime = datetime.now()
        current_timestamp = current_datetime.timestamp()
        self.db.cursor.execute(
            'INSERT INTO calendars (data, created_at, year) VALUES (?, ?, ?)',
            (json.dumps(data), current_timestamp, year,)
        )
        self.db.connection.commit()

    def get_list(self, year: int):
        current_datetime = datetime.now()
        prev = current_datetime - timedelta(hours=6)
        prev = prev.timestamp()
        self.db.cursor.execute('SELECT * FROM calendars where `year` = '+str(year)+' and created_at >= ' + str(prev))
        tasks = self.db.cursor.fetchone()
        if not tasks:
            return None
        return tasks
