# 專案架構說明

## 目錄結構

```
Document-Converter/
│
├── 前端 (Frontend)
│   └── frontend/
│       ├── templates/
│       │   └── index.html          # 主頁面
│       └── static/
│           ├── css/
│           │   └── style.css       # 樣式表
│           └── js/
│               └── app.js          # 前端邏輯
│
├── 後端 (Backend)
│   ├── app.py                      # Flask API 服務器
│   ├── config.py                   # 配置文件
│   ├── converters/                 # 轉換器模組
│   │   ├── __init__.py
│   │   ├── document_converter.py  # 文檔轉換器
│   │   └── image_converter.py     # 圖片轉換器
│   └── utils/                      # 工具模組
│       ├── __init__.py
│       └── file_detector.py       # 格式偵測器
│
├── 臨時文件 (自動生成)
│   ├── uploads/                    # 上傳文件暫存
│   └── outputs/                    # 轉換結果暫存
│
├── 舊版桌面應用 (可選)
│   └── main.py                     # CustomTkinter GUI
│
├── 配置文件
│   ├── requirements.txt            # Python 依賴
│   ├── .gitignore                  # Git 忽略規則
│   └── config.py                   # 應用配置
│
├── 啟動腳本
│   └── run_web.py                  # Web 版快速啟動
│
└── 文檔
    ├── README.md                   # 項目說明
    ├── README_WEB.md               # Web 版說明
    ├── QUICKSTART.md               # 快速開始
    └── PROJECT_ARCHITECTURE.md     # 本文件
```

## 架構設計

### 1. 前後端分離

**前端 (Frontend)**
- 純靜態 HTML/CSS/JavaScript
- 無需任何框架（Vanilla JS）
- 使用 Fetch API 與後端通信
- 支持拖放上傳
- 響應式設計
- 暗色/亮色主題

**後端 (Backend)**
- Flask RESTful API
- 處理文件上傳和轉換
- 會話管理
- 格式自動偵測

### 2. API 設計

所有 API 端點遵循 RESTful 原則：

```
GET    /                              # 主頁面
GET    /api/formats                   # 獲取支援格式
POST   /api/detect                    # 偵測文件格式
POST   /api/convert                   # 轉換文件
GET    /api/download/<id>/<file>      # 下載文件
DELETE /api/cleanup/<id>              # 清理會話
```

### 3. 數據流

```
1. 用戶選擇文件
   ↓
2. 前端上傳到 /api/detect
   ↓
3. 後端偵測格式，返回可用目標格式
   ↓
4. 用戶選擇目標格式
   ↓
5. 前端請求 /api/convert
   ↓
6. 後端執行轉換
   ↓
7. 返回下載鏈接
   ↓
8. 用戶下載文件
   ↓
9. 清理臨時文件
```

### 4. 會話管理

- 每次上傳創建一個唯一的 session_id (UUID)
- 文件存儲在 uploads/<session_id>/
- 轉換結果存儲在 outputs/<session_id>/
- 用戶可手動清理或定時清理

### 5. 錯誤處理

```python
# 統一的錯誤響應格式
{
    "success": false,
    "error": "錯誤信息"
}

# 成功響應格式
{
    "success": true,
    "data": { ... }
}
```

### 6. 安全考慮

- 文件大小限制 (50MB)
- 文件類型驗證
- 安全的文件名處理 (secure_filename)
- CORS 配置
- 輸入驗證

## 技術棧

### 前端
- HTML5
- CSS3 (CSS Variables, Flexbox, Grid)
- JavaScript ES6+
- Fetch API

### 後端
- Python 3.8+
- Flask 3.0+
- Flask-CORS
- Pillow (圖片處理)
- python-docx (Word 處理)
- openpyxl (Excel 處理)
- PyPDF2 (PDF 處理)
- python-magic (格式偵測)

### 部署
- 開發: Flask 內建服務器
- 生產: Gunicorn + Nginx

## 擴展性

### 添加新的文件格式

1. 在 `utils/file_detector.py` 中添加格式定義
2. 在相應的轉換器中實現轉換邏輯
3. 更新 API 響應

### 添加新的轉換器

1. 在 `converters/` 創建新的轉換器模組
2. 實現 `convert(input_path, output_path, format)` 方法
3. 在 `app.py` 中註冊新的轉換器

### 添加用戶認證

1. 安裝 Flask-Login
2. 實現用戶模型和認證邏輯
3. 保護需要認證的端點
4. 更新前端添加登錄表單

## 部署指南

### 開發環境

```bash
python run_web.py
```

### 生產環境

```bash
# 安裝 Gunicorn
pip install gunicorn

# 啟動服務器
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# 使用 Nginx 反向代理
# 配置文件見下方
```

### Nginx 配置示例

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # 文件上傳大小限制
        client_max_body_size 50M;
    }

    location /static {
        alias /path/to/Document-Converter/frontend/static;
        expires 30d;
    }
}
```

## 維護

### 定期清理臨時文件

創建定時任務清理超過 24 小時的文件：

```python
import os
import time
from pathlib import Path

def cleanup_old_files(directory, max_age_hours=24):
    now = time.time()
    max_age_seconds = max_age_hours * 3600
    
    for item in Path(directory).iterdir():
        if item.is_dir():
            age = now - item.stat().st_mtime
            if age > max_age_seconds:
                shutil.rmtree(item)
```

### 日誌記錄

添加日誌記錄以便調試：

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## 性能優化

1. **使用 CDN** 提供靜態資源
2. **啟用 gzip 壓縮**
3. **使用 Redis 緩存** 常用數據
4. **異步任務處理** (Celery)
5. **負載均衡** 多個 Gunicorn 工作進程

## 測試

```bash
# 運行單元測試
python -m pytest tests/

# 測試 API 端點
curl -X POST -F "file=@test.pdf" http://localhost:5000/api/detect
```
