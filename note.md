備註:

我原本是用main.py去開伺服器網站，後來照你說的改成app.py，但我不是複製你的程式碼，我是開一個新的，從我這裡原本的main.py程式下去改的

然後bridge_detector.py是你的main.py檔案，因為他是在做橋式姿勢的辨認，所以我直接複製過來改名了，目前它裡面內容我完全沒有動


簡單來說

app.py 開伺服器

bridge_detector.py 橋式偵測 (就你的檔案)

users_db.py 使用者資料庫 (用來存使用者運動的日期 次數 時間)

index.html 網站畫面的呈現


其餘檔案

add_test_data.py 當初還沒合併程式，需要測試檔案所以寫的輸入檔案程式

check_db.py 查看用戶資料庫用

init_record.py 建立使用者資料庫表 (如果想知道資料庫存什麼檔案可以看這裡的設定)

main.py 原本拿來開伺服器用的，現在沒有在用

OK
