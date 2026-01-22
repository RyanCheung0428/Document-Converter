# 更新日誌

## [2.0.0] - 2024-01-23

### 🎉 重大更新 - 重構為 Web 應用

#### ✅ 新增
- ✨ 全新的 Web 界面
- 🎨 現代化的 UI 設計
- 🌓 暗色/亮色主題支援
- 📤 拖放文件上傳
- 🔄 實時轉換進度
- 📱 響應式設計
- 🔌 RESTful API
- 📝 完整的 API 文檔

#### 🗂️ 架構重組
- 前後端分離架構
- 清晰的目錄結構
- 模組化設計
- 易於維護和擴展

#### 🔧 技術棧更新
- **前端**: HTML5, CSS3, Vanilla JavaScript
- **後端**: Flask 3.0+, Flask-CORS
- **部署**: 支援 Gunicorn + Nginx

#### 📁 新的目錄結構
```
Document-Converter/
├── app.py              # 主入口
├── backend/            # 後端代碼
│   ├── app.py
│   ├── config.py
│   ├── converters/
│   └── utils/
├── frontend/           # 前端代碼
│   ├── templates/
│   └── static/
└── docs/              # 文檔
```

#### 🗑️ 移除
- ❌ 移除舊的桌面應用 (main.py)
- ❌ 移除 PyInstaller 構建文件
- ❌ 移除過時的文檔
- ❌ 清理臨時文件和構建產物

#### 📚 新增文檔
- `README.md` - 主要文檔
- `docs/README_WEB.md` - Web 版詳細說明
- `docs/PROJECT_ARCHITECTURE.md` - 架構文檔
- `docs/STRUCTURE.md` - 目錄結構說明
- `docs/QUICK_REFERENCE.md` - 快速參考指南

#### 🚀 啟動方式
```bash
# 新的啟動方式
python run_web.py

# 或
python app.py
```

### 💡 主要改進
- 更好的代碼組織
- 更清晰的文件結構
- 更容易維護
- 更好的用戶體驗
- 更強的擴展性

---

## [1.0.0] - 2024-01-20

### 初始版本
- ✅ 桌面應用 (CustomTkinter)
- ✅ 基本文件轉換功能
- ✅ 支援多種格式
