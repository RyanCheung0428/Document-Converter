# Excel 轉 PDF 工具

這是一個簡單的 Python 工具，用於將指定資料夾內的所有 Excel (.xlsx) 文件批量轉換為 PDF 格式。

## 功能特點

- 批量轉換資料夾內的所有 xlsx 文件
- 支援自訂輸出目錄
- 顯示轉換進度和結果統計
- 自動跳過臨時文件（以 ~ 開頭的文件）

## 系統要求

- Windows 作業系統
- Python 3.7 或更高版本
- Microsoft Excel（需要安裝在系統上）

## 安裝

1. 確保已創建並激活虛擬環境：
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2. 安裝所需套件：
```bash
pip install -r requirements.txt
```

## 使用方法

### 方法 1：互動模式

直接運行程式，然後按提示輸入路徑：

```bash
python excel_to_pdf.py
```

### 方法 2：命令列參數

直接在命令列中指定資料夾路徑：

```bash
# 轉換後的 PDF 與源文件放在同一目錄
python excel_to_pdf.py "C:\path\to\excel\files"

# 指定 PDF 輸出目錄
python excel_to_pdf.py "C:\path\to\excel\files" "C:\path\to\output"
```

## 範例

```bash
# 將 D:\Documents\Excel 資料夾內的所有 xlsx 文件轉換為 PDF
python excel_to_pdf.py "D:\Documents\Excel"

# 將 xlsx 文件轉換後輸出到 D:\Documents\PDFs 資料夾
python excel_to_pdf.py "D:\Documents\Excel" "D:\Documents\PDFs"
```

## 注意事項

- 轉換過程中需要啟動 Excel 應用程式（背景運行）
- 確保 Excel 文件沒有被其他程式佔用
- 大型文件可能需要較長的轉換時間
- 轉換後的 PDF 格式和排版與 Excel 中的列印預覽一致

## 故障排除

如果遇到錯誤：

1. **找不到 Excel**：確保已安裝 Microsoft Excel
2. **pywin32 錯誤**：嘗試重新安裝 `pip install --upgrade pywin32`
3. **權限錯誤**：確保對源資料夾和輸出資料夾有讀寫權限
