# 檔案清理策略

本文檔說明 Document-Converter 的檔案自動清理機制，確保上傳和轉換的檔案不會永久儲存在伺服器上。

## 清理機制概覽

### 1. 自動定時清理
- **清理週期**: 每 30 分鐘執行一次
- **檔案保留時間**: 2 小時
- **清理對象**: `uploads/` 和 `outputs/` 目錄下超過 2 小時的 session 資料夾
- **實現位置**: `backend/app.py:68-76` 使用 APScheduler

```python
session_cleaner = SessionCleaner(
    app.config['UPLOAD_FOLDER'],
    app.config['OUTPUT_FOLDER'],
    max_age_hours=2  # 2 小時
)

scheduler.add_job(
    func=session_cleaner.cleanup_old_sessions,
    trigger="interval",
    minutes=30  # 每 30 分鐘
)
```

### 2. 頁面關閉時清理
- **觸發時機**: 使用者關閉或離開頁面
- **使用技術**: `navigator.sendBeacon` API（可靠的背景請求）
- **實現位置**: `frontend/static/js/app.js:791-802`

```javascript
window.addEventListener('beforeunload', cleanupOnUnload);

function cleanupOnUnload(event) {
    if (state.files.length > 0) {
        for (const file of state.files) {
            if (file.sessionId) {
                navigator.sendBeacon(`/api/cleanup/${file.sessionId}`);
            }
        }
    }
}
```

### 3. 頁面隱藏時延遲清理
- **觸發時機**: 使用者切換分頁或最小化視窗超過 5 分鐘
- **延遲時間**: 5 分鐘（防止誤刪正在使用的檔案）
- **實現位置**: `frontend/static/js/app.js:804-823`

```javascript
document.addEventListener('visibilitychange', handleVisibilityChange);

function handleVisibilityChange() {
    if (document.hidden) {
        // 5 分鐘後清理
        visibilityTimer = setTimeout(() => {
            // 清理所有 session
        }, 5 * 60 * 1000);
    } else {
        // 使用者回來了，取消清理
        clearTimeout(visibilityTimer);
    }
}
```

### 4. 手動清理
- **觸發時機**: 
  - 使用者點擊「新轉換」按鈕
  - 使用者點擊「清除」按鈕
- **實現位置**: `frontend/static/js/app.js:729-760`

## 下載行為

### 單檔下載
- **不會立即刪除**: 允許使用者重新下載
- **保留時間**: 依賴自動清理機制（2 小時）
- **端點**: `GET /api/download/<session_id>/<filename>`

### 批量下載
- **ZIP 檔案**: 下載後立即刪除臨時 ZIP
- **原始檔案**: 保留在 session 中，依賴自動清理
- **端點**: `POST /api/download-batch`

## API 端點

### 清理端點
```
DELETE/POST /api/cleanup/<session_id>
```
- 支援 DELETE 和 POST 方法（POST 用於 sendBeacon）
- 刪除指定 session 的上傳和輸出資料夾
- 實現位置: `backend/app.py:320-336`

### 清理統計
```
GET /api/cleanup/stats
```
- 查看當前儲存使用情況
- 返回 session 數量和總大小

### 手動觸發清理
```
POST /api/cleanup/run
```
- 立即執行一次清理任務
- 返回清理統計資訊

## 檔案生命週期

```
1. 上傳 → uploads/<session_id>/
   ↓
2. 轉換 → outputs/<session_id>/
   ↓
3. 下載（可重複）
   ↓
4. 清理觸發：
   - 頁面關閉/離開 → 立即清理
   - 隱藏 5 分鐘 → 延遲清理  
   - 超過 2 小時 → 自動清理
   - 手動操作 → 主動清理
```

## 優勢

1. **支援重新下載**: 檔案在 session 期間可多次下載
2. **自動管理**: 無需手動維護，防止儲存空間耗盡
3. **靈活性**: 多種清理機制確保檔案及時清除
4. **可靠性**: 使用 sendBeacon 確保頁面關閉時清理成功

## 配置調整

如需修改清理參數，可在 `backend/app.py` 調整：

```python
# 修改保留時間（小時）
max_age_hours=2

# 修改清理頻率（分鐘）
minutes=30
```

如需修改前端延遲清理時間，在 `frontend/static/js/app.js` 調整：

```javascript
// 修改隱藏延遲時間（毫秒）
5 * 60 * 1000  // 5 分鐘
```
