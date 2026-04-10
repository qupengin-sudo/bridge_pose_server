from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from bridge_detector import open_bridge_app
import sqlite3  # 引入資料庫工具
import json

# 建立一個 FastAPI 實體(伺服器)
app = FastAPI()

# 告訴伺服器HTML檔案都放在一個叫做 "templates" 的資料夾裡
templates = Jinja2Templates(directory="templates")

# 定義首頁路由(引導使用者去看首頁)
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    # 叫 Jinja2 去 templates 資料夾找 "index.html" 呈現出來
    return templates.TemplateResponse("index.html", {"request": request})

# --- 註冊功能 ---

@app.post("/register")
async def register(request: Request):
    # 1. 從網頁接收傳過來的 JSON 資料 (帳號密碼)
    data = await request.json()
    username = data.get("username")
    password = data.get("password")

    # 2. 連接到 users.db 資料庫
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
        # 3. 執行 SQL 指令存入資料 (把帳號密碼塞進 users 資料表)
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        
        conn.commit()
        conn.close()
        return {"status": "success", "message": "註冊成功！"}
        
    except sqlite3.IntegrityError:
        # 如果帳號重複了，會跳到這裡
        return {"status": "error", "message": "這個帳號已經有人用了喔！"}
    except Exception as e:
        # 如果發生其他錯誤 (例如資料庫檔案沒找到)
        return {"status": "error", "message": str(e)}

# --- 登入功能 ---
@app.post("/login")
async def login(request: Request):
    # 1. 接收網頁傳過來的登入資料
    data = await request.json()
    u_input = data.get("username")
    p_input = data.get("password")

    # 2. 連接到資料庫查找
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # 3. 搜尋是否有符合的帳號與密碼
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (u_input, p_input))
    user = cursor.fetchone() # 抓取一筆符合的資料
    
    conn.close()
    
    # 4. 判斷結果
    if user:
        return {"status": "success", "message": "登入成功！歡迎回來"}
    else:
        return {"status": "error", "message": "帳號或密碼錯誤，請再試一次"}

# # --- 啟動橋式偵測與存檔 ---
# @app.post("/open_app")
# async def open_app(request: Request):
#     # 1. 先從網頁接收是誰在運動 (避免網頁等待超時)
#     data = await request.json()
#     u = data.get("username")

#     # 2. 呼叫：開啟鏡頭、彈出計時選單 (程式會在這裡等你運動完)
#     countdown, bridge_count = open_bridge_app()
    
#     # 3. 運動結束：整理成績準備存檔
#     c = bridge_count
#     e = 0
#     d = countdown
    
#     conn = sqlite3.connect('users.db')
#     cursor = conn.cursor()
#     # 將數據插入到 records 資料表
#     cursor.execute("INSERT INTO records (username, correct_count, error_count, duration_seconds) VALUES (?, ?, ?, ?)", (u, c, e, d))
#     conn.commit()
#     conn.close()
    
#     return {"status": "success"}

# # --- 新增：儲存運動紀錄功能 ---

# @app.post("/save_record")
# async def save_record(request: Request):
#     data = await request.json()
#     u = data.get("username")
#     c = data.get("correct")
#     e = data.get("error")
#     d = data.get("duration") # 從網頁拿到的運動總秒數
    
#     conn = sqlite3.connect('users.db')
#     cursor = conn.cursor()
#     # 將數據插入到 records 資料表 (包含新增的 duration_seconds 欄位)
#     cursor.execute("INSERT INTO records (username, correct_count, error_count, duration_seconds) VALUES (?, ?, ?, ?)", (u, c, e, d))
#     conn.commit()
#     conn.close()
#     return {"status": "success"}


# --- 🚀 核心合體：啟動橋式偵測與存檔 ---
@app.post("/open_app")
async def open_app(request: Request):
    # 1. 先從網頁接收是誰在運動 (訪客的話 username 會是空字串或 null)
    data = await request.json()
    u = data.get("username", "") 

    # 2. 呼叫大廚：開啟鏡頭、彈出計時選單 (程式會在這裡等你運動完)
    # open_bridge_app 預計會回傳 (總秒數, 正確次數)
    countdown, bridge_count = open_bridge_app()
    
    # ✅ 守門員機制：只有在「有登入(u不為空)」且「有做運動(count>0)」才直接存檔
    if u and bridge_count > 0:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        # 將數據插入到 records 資料表
        cursor.execute("INSERT INTO records (username, correct_count, error_count, duration_seconds) VALUES (?, ?, ?, ?)", 
                       (u, bridge_count, 0, countdown))
        conn.commit()
        conn.close()
        print(f"系統：已為使用者 {u} 自動存檔紀錄。")
    
    # ✅ 重要：不管有沒有存入資料庫，都要把成績傳回給網頁
    # 這樣訪客才能在登入後，靠網頁把這兩組數字傳給 /save_record
    return {
        "status": "success", 
        "duration": countdown, 
        "correct_count": bridge_count
    }

# --- 儲存運動紀錄功能 (用於訪客登入後的「補存檔」) ---
@app.post("/save_record")
async def save_record(request: Request):
    data = await request.json()
    u = data.get("username")
    c = data.get("correct")
    e = data.get("error")
    d = data.get("duration") 
    
    # ✅ 守門員機制：確認次數大於 0 才允許補存
    if u and c > 0:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO records (username, correct_count, error_count, duration_seconds) VALUES (?, ?, ?, ?)", 
                       (u, c, e, d))
        conn.commit()
        conn.close()
        return {"status": "success", "message": "紀錄補存成功"}
    
    return {"status": "error", "message": "無效資料或未登入"}

# 週紀錄統計功能 長條圖

@app.get("/get_weekly_stats/{username}")
async def get_weekly_stats(username: str):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # 抓取該使用者最近 7 次的運動日期、次數、時間
    cursor.execute("""
        SELECT strftime('%m-%d', timestamp) as day, 
               correct_count, error_count, duration_seconds
        FROM records 
        WHERE username = ? 
        ORDER BY timestamp DESC 
        LIMIT 7
    """, (username,))
    
    rows = cursor.fetchall()
    conn.close()
    
    # 資料反轉 日期由遠到近排列
    reversed_rows = rows[::-1]
    
    labels = [r[0] for r in reversed_rows]    # 日期 (月-日)
    corrects = [r[1] for r in reversed_rows]  # 正確次數
    errors = [r[2] for r in reversed_rows]    # 錯誤次數 
    durations = [r[3] for r in reversed_rows] # 運動秒數 
    
    return {"labels": labels, "corrects": corrects, "errors": errors, "durations": durations}

if __name__ == "__main__":
    import uvicorn
    # 啟動伺服器：網址是 127.0.0.1，通訊埠(port)是 8000
    uvicorn.run(app, host="127.0.0.1", port=8000)