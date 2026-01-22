# 專案目錄結構

```
Document-Converter/
│
├── 📄 app.py                          # 主入口文件
├── 📄 run_web.py                      # Python 啟動腳本
├── 📄 run_web.bat                     # Windows 啟動腳本
├── 📄 requirements.txt                # Python 依賴列表
├── 📄 README.md                       # 專案說明文檔
├── 📄 .gitignore                      # Git 忽略規則
│
├── 📁 backend/                        # 後端目錄
│   ├── 📄 app.py                      # Flask REST API 服務器
│   ├── 📄 config.py                   # 應用配置
│   │
│   ├── 📁 converters/                 # 轉換器模組
│   │   ├── 📄 __init__.py
│   │   ├── 📄 document_converter.py  # 文檔轉換 (PDF, DOCX, XLSX)
│   │   └── 📄 image_converter.py     # 圖片轉換 (PNG, JPG, etc.)
│   │
│   └── 📁 utils/                      # 工具模組
│       ├── 📄 __init__.py
│       └── 📄 file_detector.py       # 文件格式自動偵測
│
├── 📁 frontend/                       # 前端目錄
│   ├── 📁 templates/
│   │   └── 📄 index.html             # 主頁面 HTML
│   │
│   └── 📁 static/
│       ├── 📁 css/
│       │   └── 📄 style.css          # 樣式表 (支援暗色/亮色模式)
│       │
│       └── 📁 js/
│           └── 📄 app.js             # 前端邏輯 (上傳、轉換、下載)
│
├── 📁 docs/                           # 文檔目錄
│   ├── 📄 README_WEB.md              # Web 版詳細說明
│   └── 📄 PROJECT_ARCHITECTURE.md     # 架構設計文檔
│
├── 📁 uploads/                        # 上傳文件暫存 (自動生成)
│   └── 📁 <session_id>/              # 按會話 ID 分類存儲
│
└── 📁 outputs/                        # 轉換結果暫存 (自動生成)
    └── 📁 <session_id>/              # 按會話 ID 分類存儲
```

## 📝 文件說明

### 根目錄文件

| 文件 | 說明 |
|------|------|
| `app.py` | 應用主入口，導入並運行 Flask 服務器 |
| `run_web.py` | 啟動腳本，自動檢查依賴並啟動服務器 |
| `run_web.bat` | Windows 批處理啟動腳本 |
| `requirements.txt` | Python 依賴包列表 |
| `README.md` | 專案主要文檔 |
| `.gitignore` | Git 版本控制忽略規則 |

### Backend 目錄

| 文件/目錄 | 說明 |
|-----------|------|
| `backend/app.py` | Flask REST API 服務器主文件 |
| `backend/config.py` | 配置管理 (開發/生產環境) |
| `backend/converters/` | 文件轉換器模組 |
| `backend/utils/` | 工具函數模組 |

#### Converters 模組

- `document_converter.py`: 處理文檔格式轉換
  - PDF ↔ DOCX
  - PDF ↔ XLSX
  - DOCX → PDF
  - XLSX → PDF

- `image_converter.py`: 處理圖片格式轉換
  - PNG, JPG, JPEG, BMP, TIFF, GIF, WEBP, ICO 互轉
  - 圖片 → PDF

#### Utils 模組

- `file_detector.py`: 自動偵測文件格式
  - 使用 magic bytes 識別
  - 支援多種 MIME 類型
  - 返回可轉換的目標格式列表

### Frontend 目錄

| 文件/目錄 | 說明 |
|-----------|------|
| `templates/index.html` | 主頁面 HTML 結構 |
| `static/css/style.css` | 樣式表，支援主題切換 |
| `static/js/app.js` | 前端邏輯，處理上傳和轉換 |

### Docs 目錄

| 文件 | 說明 |
|------|------|
| `README_WEB.md` | Web 版詳細使用說明 |
| `PROJECT_ARCHITECTURE.md` | 技術架構文檔 |

## 🔄 數據流程

```
用戶操作
   ↓
前端 (index.html + app.js)
   ↓
HTTP 請求 (Fetch API)
   ↓
後端 API (backend/app.py)
   ↓
文件處理
   ├── file_detector.py (格式偵測)
   ├── document_converter.py (文檔轉換)
   └── image_converter.py (圖片轉換)
   ↓
返回結果
   ↓
前端顯示
```

## 🎯 各模組職責

### 前端 (Frontend)
- ✅ 用戶界面呈現
- ✅ 文件拖放上傳
- ✅ 主題切換
- ✅ 進度顯示
- ✅ 結果展示

### 後端 (Backend)
- ✅ RESTful API 端點
- ✅ 文件上傳處理
- ✅ 格式自動偵測
- ✅ 文件格式轉換
- ✅ 會話管理
- ✅ 錯誤處理

### 轉換器 (Converters)
- ✅ 文檔格式轉換邏輯
- ✅ 圖片格式轉換邏輯
- ✅ 轉換參數配置

### 工具 (Utils)
- ✅ 文件格式偵測
- ✅ 通用工具函數

## 📊 代碼統計

```
總文件數: 12 個 Python/HTML/CSS/JS 文件
代碼行數: 約 1,500 行
支援格式: 13 種
API 端點: 6 個
```

## 🔧 擴展指南

### 添加新的文件格式支援

1. 在 `backend/utils/file_detector.py` 添加 MIME 類型映射
2. 在對應的轉換器中實現轉換邏輯
3. 更新 `get_conversion_targets()` 方法

### 添加新的轉換器

1. 在 `backend/converters/` 創建新的轉換器文件
2. 實現 `convert(input_path, output_path, format)` 方法
3. 在 `backend/app.py` 中註冊並使用

### 添加新的 API 端點

1. 在 `backend/app.py` 添加路由
2. 實現處理邏輯
3. 更新前端 `app.js` 調用新端點

## 🧹 維護建議

- ⏰ 定期清理 `uploads/` 和 `outputs/` 目錄
- 📝 查看日誌文件排查問題
- 🔄 定期更新依賴包
- 🔒 定期檢查安全漏洞
