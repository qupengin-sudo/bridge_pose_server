import sqlite3
import random
from datetime import datetime, timedelta

conn = sqlite3.connect('users.db', timeout=5)
cursor = conn.cursor()

cursor.execute("SELECT id FROM users WHERE username = ? AND password = ?", ("test", "123"))
if not cursor.fetchone():
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("test", "123"))
    print("使用者 test 已建立")
else:
    print("使用者 test 已存在")

now = datetime.now()
for day_offset in range(7):
    day = now - timedelta(days=6 - day_offset)
    sessions = random.randint(1, 3)
    for _ in range(sessions):
        correct = random.randint(3, 20)
        error = random.randint(0, 8)
        duration = random.randint(60, 300)
        hour = random.randint(8, 22)
        minute = random.randint(0, 59)
        ts = day.replace(hour=hour, minute=minute, second=random.randint(0, 59))
        cursor.execute(
            "INSERT INTO records (username, correct_count, error_count, duration_seconds, timestamp) VALUES (?, ?, ?, ?, ?)",
            ("test", correct, error, duration, ts.strftime('%Y-%m-%d %H:%M:%S'))
        )

conn.commit()
conn.close()
print("已新增 7 天隨機紀錄，請登入 test/123 查看")
