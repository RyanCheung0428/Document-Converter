# 快速參考指南

## 📝 常用命令

### 啟動應用

```bash
# 方法 1: 使用啟動腳本 (推薦)
python run_web.py

# 方法 2: 直接運行
python app.py

# 方法 3: Windows 批處理
run_web.bat
```

### 開發模式

```bash
# 開發模式 (自動重載)
export FLASK_ENV=development
python app.py
```

### 生產模式

```bash
# 使用 Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 🔌 API 快速參考

### 獲取支援格式
```bash
curl http://localhost:5000/api/formats
```

### 上傳並偵測文件
```bash
curl -X POST -F "file=@example.pdf" http://localhost:5000/api/detect
```

### 轉換文件
```bash
curl -X POST http://localhost:5000/api/convert \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "your-session-id",
    "filename": "example.pdf",
    "target_format": "docx"
  }'
```

### 下載文件
```bash
curl http://localhost:5000/api/download/session-id/example.docx -o example.docx
```

### 清理會話
```bash
curl -X DELETE http://localhost:5000/api/cleanup/session-id
```

## 📁 目錄說明

```
/                       # 根目錄
├── app.py             # 主入口 (運行這個文件)
├── backend/           # 後端代碼
│   ├── app.py        # Flask API
│   ├── converters/   # 轉換器
│   └── utils/        # 工具
├── frontend/          # 前端代碼
│   ├── templates/    # HTML 模板
│   └── static/       # CSS/JS 靜態文件
├── docs/             # 文檔
├── uploads/          # 臨時上傳 (自動生成)
└── outputs/          # 轉換結果 (自動生成)
```

## 🔧 常見問題

### 1. 如何更改端口？

編輯 `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=8080)  # 改為 8080
```

### 2. 如何增加文件大小限制？

編輯 `backend/config.py`:
```python
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 改為 100MB
```

### 3. 如何添加新的文件格式？

1. 在 `backend/utils/file_detector.py` 添加 MIME 類型
2. 在轉換器中實現轉換邏輯
3. 更新可用目標格式列表

### 4. 如何清理臨時文件？

```bash
# Linux/Mac
rm -rf uploads/* outputs/*

# Windows
rmdir /s /q uploads
rmdir /s /q outputs
mkdir uploads
mkdir outputs
```

### 5. 如何啟用 HTTPS？

使用 Nginx 反向代理或生成 SSL 證書:
```bash
# 使用 Let's Encrypt
certbot --nginx -d your-domain.com
```

## 🎨 自定義主題

編輯 `frontend/static/css/style.css`:

```css
:root {
    --primary-color: #your-color;  /* 主色調 */
    --background: #your-bg;        /* 背景色 */
}
```

## 📦 依賴更新

```bash
# 查看過期的包
pip list --outdated

# 更新所有包
pip install --upgrade -r requirements.txt

# 生成新的 requirements
pip freeze > requirements.txt
```

## 🐛 調試技巧

### 啟用調試模式
```python
app.run(debug=True)  # 顯示詳細錯誤信息
```

### 查看日誌
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 測試 API
使用 Postman 或 curl 測試各個端點

## 🚀 性能優化

### 1. 使用緩存
```python
from flask_caching import Cache
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
```

### 2. 壓縮響應
```python
from flask_compress import Compress
Compress(app)
```

### 3. 異步任務
```python
from celery import Celery
# 處理長時間運行的轉換任務
```

## 📊 監控

### 健康檢查端點
添加到 `backend/app.py`:
```python
@app.route('/health')
def health():
    return jsonify({'status': 'ok'})
```

### 訪問日誌
```bash
gunicorn --access-logfile access.log app:app
```

## 🔐 安全建議

1. ✅ 設置 SECRET_KEY 環境變量
2. ✅ 限制文件大小
3. ✅ 驗證文件類型
4. ✅ 使用 HTTPS
5. ✅ 定期清理臨時文件
6. ✅ 實施速率限制

## 📞 獲取幫助

- 查看文檔: `docs/`
- 檢查日誌: 查看控制台輸出
- 測試 API: 使用 curl 或 Postman
- 提交 Issue: GitHub Issues

---

**快速開始**: `python run_web.py` 🚀
