# 橋式運動追蹤系統

即時偵測橋式動作的運動追蹤系統，透過攝影機與 MediaPipe 姿態辨識技術，自動計算動作次數並記錄訓練數據。

## 功能特色

- **即時姿態偵測**：透過攝影機擷取畫面，利用 MediaPipe 計算膝-髖-肩角度，判斷橋式動作階段
- **三階段狀態機**：
  - STAGE1（綠色）：完成橋式，角度 155°–180°
  - TRANSITION（紅色）：過渡階段，角度 130°–154°
  - STAGE2（橘色）：休息階段，角度 < 130°
- **自訂訓練時間**：透過分/秒選擇器自由設定訓練時長
- **帳號系統**：註冊、登入、Cookie 持久化（30 天免重新登入）
- **訓練紀錄**：自動儲存每次訓練的次數與時長
- **數據視覺化**：堆疊長條圖顯示每日訓練統計，支援 1–50 天回顧
- **進階搜尋**：依日期範圍、運動時長篩選紀錄
- **分頁瀏覽**：完整訓練歷史紀錄，每頁 20 筆

## 系統架構

| 元件 | 技術 |
|------|------|
| 後端 | FastAPI + Uvicorn |
| 前端 | HTML + Chart.js |
| 資料庫 | SQLite |
| 姿態偵測 | MediaPipe + OpenCV |
| 桌面對話框 | Tkinter |
| 設定檔 | config.json |

## 檔案結構

```
bridge_pose_server/
├── app.py                    # FastAPI 主程式，API 端點
├── bridge_detector.py        # 姿態偵測核心模組
├── init_record.py            # 資料庫初始化
├── config.json               # 設定檔（攝影機 ID、角度範圍）
├── pose_landmarker_lite.task # MediaPipe 模型檔
├── add_test_data.py          # 測試資料產生工具
├── templates/
│   └── index.html            # 前端頁面
└── users.db                  # SQLite 資料庫（自動建立）
```

## 安裝與執行

### 前置需求

- Python 3.x
- 攝影機裝置

### 安裝依賴

```bash
pip install fastapi uvicorn mediapipe opencv-python numpy
```

### 啟動伺服器

```bash
python app.py
```

伺服器會在 `http://127.0.0.1:8000` 啟動，資料庫會在首次啟動時自動建立。

## 設定檔

`config.json` 可調整以下參數：

```json
{
    "DEVICE_ID": 2,
    "STAGE1_MIN": 155,
    "STAGE1_MAX": 180,
    "STAGE2_MAX": 130
}
```

| 參數 | 說明 |
|------|------|
| `DEVICE_ID` | 攝影機裝置編號 |
| `STAGE1_MIN` | 完成橋式的最小角度（膝-髖-肩） |
| `STAGE1_MAX` | 完成橋式的最大角度 |
| `STAGE2_MAX` | 休息階段的最大角度，低於此值為休息 |

## API 端點

### 認證

| 方法 | 路徑 | 說明 |
|------|------|------|
| GET | `/` | 首頁 |
| POST | `/register` | 註冊帳號 |
| POST | `/login` | 登入 |
| GET | `/me` | 檢查登入狀態 |
| POST | `/logout` | 登出 |

### 運動與紀錄

| 方法 | 路徑 | 說明 |
|------|------|------|
| POST | `/open_app` | 啟動橋式偵測 |
| POST | `/save_record` | 補存紀錄（訪客登入後使用） |
| GET | `/get_daily_stats/{username}` | 取得每日統計（支援 `days` 參數） |
| GET | `/get_all_records/{username}` | 分頁取得所有紀錄 |
| GET | `/search_records/{username}` | 進階搜尋紀錄 |

## 資料庫結構

### users 資料表

| 欄位 | 型別 | 說明 |
|------|------|------|
| id | INTEGER | 主鍵 |
| username | TEXT | 帳號（唯一） |
| password | TEXT | 密碼 |

### records 資料表

| 欄位 | 型別 | 說明 |
|------|------|------|
| id | INTEGER | 主鍵 |
| username | TEXT | 帳號 |
| correct_count | INTEGER | 正確次數 |
| error_count | INTEGER | 錯誤次數 |
| duration_seconds | INTEGER | 訓練時長（秒） |
| timestamp | DATETIME | 建立時間（UTC） |
