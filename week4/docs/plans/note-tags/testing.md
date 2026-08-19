# Testing: Note tags 解析與儲存

Given/When/Then 情境，對應 `tasks.md` 每個任務至少一個情境。

## 對應「解析邏輯」任務（`extract_tags` 單元測試，code-agent 於 `test_extract.py` 實作）

### 情境：content 含多個不同 `#tag`
- Given: 文字內容為 `"Plan trip #urgent #followup rest of note"`
- When: 呼叫 `extract_tags(text)`
- Then: 回傳 `["urgent", "followup"]`（依出現順序，不含 `#`）

### 情境：同一個 tag 重複出現只算一次
- Given: 文字內容為 `"#urgent something #urgent again"`
- When: 呼叫 `extract_tags(text)`
- Then: 回傳 `["urgent"]`（去重，保留第一次出現的位置）

### 情境：大小寫不同的同一個 tag 視為同一個
- Given: 文字內容為 `"#Urgent later #urgent again"`
- When: 呼叫 `extract_tags(text)`
- Then: 回傳 `["urgent"]`（正規化為小寫後去重）

### 情境：content 沒有任何 `#tag`
- Given: 文字內容為 `"just a plain note without hashtags"`
- When: 呼叫 `extract_tags(text)`
- Then: 回傳 `[]`

### 情境：單獨的 `#` 或 `#` 後面不是合法字元不算 tag
- Given: 文字內容為 `"broken tag: # and #! and # trailing"`
- When: 呼叫 `extract_tags(text)`
- Then: 回傳 `[]`（`#` 後面必須緊接至少一個合法字元才算一個 tag）

## 對應「API 串接」任務（整合測試，code-agent 於 `test_notes.py` 實作）

### 情境：建立含 `#tag` 的 note 時自動解析並存下標籤
- Given: 使用者準備建立一則 `content` 包含 `"#urgent #followup"` 的 note
- When: 呼叫 `POST /notes/`，payload 為 `{"title": "...", "content": "...#urgent #followup..."}`
- Then: 回應狀態碼 201，回應 body 的 `tags` 欄位包含 `["urgent", "followup"]`

### 情境：建立不含 `#tag` 的 note 時 tags 為空陣列
- Given: 使用者建立一則 `content` 完全沒有 `#` 的 note
- When: 呼叫 `POST /notes/`
- Then: 回應 body 的 `tags` 欄位為 `[]`（不是 `null`）

### 情境：`GET /notes/{id}` 讀回的 note 也帶有先前存下的 tags
- Given: 已用含 `#followup` content 建立過一則 note，取得其 `id`
- When: 呼叫 `GET /notes/{id}`
- Then: 回應 body 的 `tags` 欄位包含 `["followup"]`（證明 tags 是「存到 DB」而不是只在 create 當下算一次
  就丟掉）

## 對應「Schema / 儲存層」任務（db-agent 需確認的情境，可用手動驗證或另加測試覆蓋）

### 情境：全新環境（無既有 `data/app.db`）啟動後表結構含 `tags`
- Given: 移除或尚未產生本機 `data/app.db`
- When: 執行 `make seed`（或啟動 app 觸發 `apply_seed_if_needed`）
- Then: 產生的 `notes` 表包含 `tags` 欄位，且透過 `seed.sql` 插入的既有兩筆種子 note 也能正常讀出（其
  `tags` 為預設值 `[]`，不會因為 `NOT NULL` 卻沒帶值而插入失敗）

### 情境：已存在、且是舊結構（沒有 `tags` 欄位）的 `data/app.db` 不會讓 app 啟動或建立 note 直接壞掉
- Given: 一份改動前建立、`notes` 表沒有 `tags` 欄位的舊 `data/app.db`
- When: 套用 db-agent 選定的相容策略後啟動 app，並呼叫 `POST /notes/` 建立一則新 note
- Then: 不應出現 `OperationalError: no such column: notes.tags`；新建立的 note 能正常存入並帶有解析出
  的 `tags`（若 db-agent 選擇的是「不自動 migration、要求手動重建」策略，則此情境改為驗證：文件/交接
  資訊有清楚寫明需要先刪除舊 `data/app.db` 並重新 `make seed`）

## 對應「收尾檢查」任務（refactor-agent）

### 情境：既有 `extract_action_items` 行為不受新增 `extract_tags` 影響
- Given: `backend/tests/test_extract.py` 裡原本針對 `extract_action_items` 的測試（含 `TODO:`/`!`
  結尾的判斷）
- When: 執行 `make test`
- Then: 原有 `test_extract_action_items` 依然通過，未因新增 `extract_tags` 或共用 helper 抽取而改變
  行為

### 情境：`make format && make lint` 在改動後仍通過
- Given: `extract.py`、`models.py`、`schemas.py`、`routers/notes.py` 都已依 `tasks.md` 改完
- When: 執行 `make format && make lint`
- Then: 兩者皆無錯誤退出（exit code 0），且沒有為了單純過 lint 而改變 `extract_tags`/
  `extract_action_items` 的對外行為
