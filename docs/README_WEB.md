# Universal File Converter - Web Version

這是一個基於 Web 的通用文件格式轉換器，支援多種文件格式之間的轉換。

## 架構

### 前端 (Frontend)
- **技術棧**: HTML5, CSS3, JavaScript (Vanilla)
- **位置**: `frontend/` 目錄
- **功能**:
  - 現代化的響應式介面
  - 拖放上傳文件
  - 暗色/亮色主題切換
  - 即時轉換進度顯示
  - 文件下載

### 後端 (Backend)
- **技術棧**: Python Flask REST API
- **位置**: `app.py`
- **功能**:
  - 文件上傳處理
  - 格式自動偵測
  - 文件格式轉換
  - RESTful API 端點

## 安裝

1. 安裝依賴:
```bash
pip install -r requirements.txt
```

2. 啟動開發服務器:
```bash
python app.py
```

3. 在瀏覽器訪問:
```
http://localhost:5000
```

## API 端點

### GET `/`
返回主頁面

### GET `/api/formats`
獲取所有支援的格式
```json
{
  "success": true,
  "formats": {
    "document": ["docx", "doc", "xlsx", "xls", "pdf"],
    "image": ["png", "jpg", "jpeg", "bmp", "tiff", "gif", "webp", "ico"]
  }
}
```

### POST `/api/detect`
上傳文件並偵測格式
- **Request**: multipart/form-data with file
- **Response**:
```json
{
  "success": true,
  "session_id": "uuid",
  "filename": "example.pdf",
  "detected_type": "document",
  "detected_format": "pdf",
  "available_targets": ["docx", "xlsx", "png", "jpg"]
}
```

### POST `/api/convert`
轉換文件
- **Request**:
```json
{
  "session_id": "uuid",
  "filename": "example.pdf",
  "target_format": "docx"
}
```
- **Response**:
```json
{
  "success": true,
  "output_filename": "example.docx",
  "download_url": "/api/download/uuid/example.docx"
}
```

### GET `/api/download/<session_id>/<filename>`
下載轉換後的文件

### DELETE `/api/cleanup/<session_id>`
清理會話文件

## 支援的格式

### 文檔類
- PDF ↔ DOCX, XLSX, PNG, JPG
- DOCX ↔ PDF
- XLSX ↔ PDF

### 圖片類
- PNG, JPG, JPEG, BMP, TIFF, GIF, WEBP, ICO 之間互相轉換
- 圖片 → PDF

## 生產環境部署

使用 Gunicorn 部署:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 專案結構

```
Document-Converter/
├── app.py                      # Flask 後端 API
├── main.py                     # 舊版桌面應用（可選）
├── requirements.txt            # Python 依賴
├── converters/                 # 轉換器模組
│   ├── document_converter.py
│   └── image_converter.py
├── utils/                      # 工具模組
│   └── file_detector.py
├── frontend/                   # 前端文件
│   ├── templates/
│   │   └── index.html
│   └── static/
│       ├── css/
│       │   └── style.css
│       └── js/
│           └── app.js
├── uploads/                    # 上傳文件暫存（自動創建）
└── outputs/                    # 輸出文件暫存（自動創建）
```

## 特色功能

- ✅ 自動格式偵測
- ✅ 拖放上傳
- ✅ 響應式設計
- ✅ 暗色模式支援
- ✅ RESTful API
- ✅ 會話管理
- ✅ 錯誤處理
- ✅ 進度顯示

## 注意事項

- 最大文件大小: 50MB
- 會話文件需要定期清理
- Word 轉 PDF 需要安裝 LibreOffice 或 Microsoft Word
