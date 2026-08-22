# Testing scenarios: Request validation and error handling

狀態碼標記為 `<驗證錯誤狀態碼>` 的情境,實際數字依 `design.md` 待確認③的確認結果決定(FastAPI 預設
422,或加了自訂 exception handler 後的 400)。寫測試前請先確認這一點,不要自行選一個硬寫。

### 情境:建立 title 為空字串的 note 應驗證失敗
- Given: 使用者準備建立一則 note,`title` 為 `""`,`content` 為正常非空字串
- When: 呼叫 `POST /notes/`
- Then: 回應狀態碼為 `<驗證錯誤狀態碼>`(422 或 400,依待確認③),且該筆 note 沒有被寫入(後續
  `GET /notes/` 不會多出這筆資料)

### 情境:建立 content 為空字串的 note 應驗證失敗
- Given: 使用者準備建立一則 note,`content` 為 `""`,`title` 為正常非空字串
- When: 呼叫 `POST /notes/`
- Then: 回應狀態碼為 `<驗證錯誤狀態碼>`,且該筆 note 沒有被寫入

### 情境:建立 description 為空字串的 action item 應驗證失敗
- Given: 使用者準備建立一個 action item,`description` 為 `""`
- When: 呼叫 `POST /action-items/`
- Then: 回應狀態碼為 `<驗證錯誤狀態碼>`,且該筆 action item 沒有被寫入

### 情境:查詢不存在的 note 應回 404(現況已正確,補測試覆蓋)
- Given: 資料庫裡不存在 id 為某個未使用數字(例如目前最大 id + 1,或直接用一個確定沒建立過的 id)的 note
- When: 呼叫 `GET /notes/{不存在的note_id}`
- Then: 回應狀態碼為 404,回應內容包含類似 "Note not found" 的訊息

### 情境:對不存在的 action item 呼叫 complete 應回 404(現況已正確,補測試覆蓋)
- Given: 資料庫裡不存在某個 id 的 action item
- When: 呼叫 `PUT /action-items/{不存在的item_id}/complete`
- Then: 回應狀態碼為 404,回應內容包含類似 "Action item not found" 的訊息

### (待確認①,暫不實作)情境:更新/刪除不存在的 note 應回 404
- 前提:`PUT /notes/{id}`、`DELETE /notes/{id}` 目前程式碼裡不存在(屬於 `docs/TASKS.md` 第 5 項任務)。
- 若使用者確認要把這兩個 endpoint 的存在性檢查也納入本次任務,情境會是:
  - Given: 資料庫裡不存在某個 id 的 note
  - When: 呼叫 `PUT /notes/{不存在的note_id}` 或 `DELETE /notes/{不存在的note_id}`
  - Then: 回應狀態碼為 404
  - 但這需要先把第 5 項的 endpoint 實作出來才能寫這個測試,不在本次任務單獨可完成的範圍內,列在此處
    僅供確認後續是否要擴大範圍。

### (待確認②,暫不實作)情境:建立 title 為全空白字串的 note 應驗證失敗
- 若使用者確認「全空白視為空」也要擋:
  - Given: 使用者準備建立一則 note,`title` 為 `"   "`(全空白,長度不是 0)
  - When: 呼叫 `POST /notes/`
  - Then: 回應狀態碼為 `<驗證錯誤狀態碼>`
- 若使用者確認只擋純空字串 `""`,則此情境不需要,`"   "` 應視為合法輸入並回 201。
