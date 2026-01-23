# Universal File Converter - Web 版本

🌐 一個現代化、基於 Web 的通用文件格式轉換器，支援多種文件格式之間的轉換。

## ✨ 特色功能

- 🎨 **現代化界面** - 簡潔美觀的用戶界面，支援暗色/亮色模式
- 📤 **拖放上傳** - 直接拖放文件到網頁即可上傳
- 🔍 **自動偵測** - 自動識別文件格式類型
- ⚡ **快速轉換** - 高效的文件格式轉換
- 📱 **響應式設計** - 完美支援桌面和移動設備
- 🔒 **安全可靠** - 文件大小限制和格式驗證

## 🚀 快速開始

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 啟動應用

**方法 1: 使用啟動腳本 (Windows)**
```bash
run_web.bat
```

**方法 2: 使用 Python 腳本**
```bash
python run_web.py
```

**方法 3: 直接運行**
```bash
python app.py
```

### 3. 訪問應用

在瀏覽器中打開: `http://localhost:5000`

## 📁 專案結構

```
Document-Converter/
│
├── app.py                      # 主入口文件
├── run_web.py                  # 啟動腳本 (Python)
├── run_web.bat                 # 啟動腳本 (Windows)
├── requirements.txt            # Python 依賴
├── .gitignore                  # Git 忽略規則
│
├── backend/                    # 後端目錄
│   ├── app.py                  # Flask API 服務器
│   ├── config.py               # 配置管理
│   ├── converters/             # 轉換器模組
│   │   ├── __init__.py
│   │   ├── document_converter.py
│   │   └── image_converter.py
│   └── utils/                  # 工具模組
│       ├── __init__.py
│       └── file_detector.py
│
├── frontend/                   # 前端目錄
│   ├── templates/
│   │   └── index.html         # 主頁面
│   └── static/
│       ├── css/
│       │   └── style.css      # 樣式表
│       └── js/
│           └── app.js         # 前端邏輯
│
├── docs/                       # 文檔目錄
│   ├── README_WEB.md          # Web 版詳細說明
│   └── PROJECT_ARCHITECTURE.md # 架構文檔
│
├── uploads/                    # 上傳文件暫存 (自動生成)
└── outputs/                    # 轉換結果暫存 (自動生成)
```

## 📝 支援的格式

### 文檔類（純 Python，無需外部依賴）
- **PDF** ↔ DOCX, TXT, PNG, JPG
- **DOCX** ↔ PDF, TXT, MD
- **TXT/MD** ↔ PDF, DOCX
- **XLSX/XLSM** ↔ PDF, CSV
- **CSV** → PDF, XLSX

### 圖片類
- **PNG, JPG, JPEG, BMP, TIFF, GIF, WEBP, ICO** 之間互相轉換
- **圖片** → PDF

### 注意事項
- 所有轉換均使用純 Python 實現，無需安裝 LibreOffice 或 Microsoft Office
- XLSM 轉換至 XLSX/CSV/PDF 時會丟失 VBA 宏
- 不支援舊格式（.doc, .xls, .rtf）- 請先在本機用 Office/LibreOffice 轉換成現代格式後再上傳

## 🔧 API 端點

| 方法 | 路徑 | 說明 |
|------|------|------|
| GET | `/` | 主頁面 |
| GET | `/api/formats` | 獲取支援的格式 |
| POST | `/api/detect` | 上傳並偵測文件格式 |
| POST | `/api/convert` | 轉換文件 |
| GET | `/api/download/<session_id>/<filename>` | 下載轉換後的文件 |
| DELETE | `/api/cleanup/<session_id>` | 清理會話文件 |

## 🛠️ 技術棧

### 前端
- HTML5
- CSS3 (CSS Variables, Flexbox, Grid)
- JavaScript (Vanilla JS)
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

## 📦 生產環境部署

### 使用 Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### 使用 Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

### Nginx 反向代理配置

```nginx
server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## ⚙️ 配置說明

### 環境變量

- `FLASK_ENV` - 運行環境 (development/production)
- `SECRET_KEY` - Flask 密鑰 (生產環境必須設置)
- `MAX_CONTENT_LENGTH` - 最大文件大小 (默認 50MB)

### 自定義配置

編輯 `backend/config.py` 文件來修改配置:

```python
class Config:
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
    UPLOAD_FOLDER = 'uploads'
    OUTPUT_FOLDER = 'outputs'
```

## 📚 更多文檔

- [Web 版詳細說明](docs/README_WEB.md)
- [專案架構文檔](docs/PROJECT_ARCHITECTURE.md)

## 🔒 安全注意事項

- 文件大小限制: 50MB
- 支援的文件類型驗證
- 安全的文件名處理
- 定期清理臨時文件
- 生產環境請設置 SECRET_KEY

## 🐛 故障排除

### 問題: 無法啟動服務器
**解決方案**: 
```bash
pip install -r requirements.txt
```

### 問題: Word 轉 PDF 失敗
**解決方案**: 需要安裝 LibreOffice 或 Microsoft Word

### 問題: 文件上傳失敗
**解決方案**: 檢查文件大小是否超過 50MB 限制

## 📄 授權

MIT License

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

## 📧 聯繫方式

如有問題或建議，請通過 GitHub Issues 聯繫。

---

**享受使用 Universal File Converter！** 🎉
