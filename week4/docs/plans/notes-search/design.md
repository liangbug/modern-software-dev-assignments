# Design: Add search endpoint for notes (docs/TASKS.md #2)

## 任務目標

`GET /notes/search/` endpoint 已存在（`backend/app/routers/notes.py:28-38`），現況與缺口：

- 查詢邏輯用 `Note.title.contains(q) | Note.content.contains(q)`，底層轉成 SQL `LIKE '%q%'`。
  在 SQLite 上 `LIKE` 對 ASCII 預設就是 case-insensitive，所以「混合大小寫查詢」現在多半也會
  查得到結果——但這是**依賴 SQLite 特定的預設 collation 行為**，不是程式碼裡顯式表達的意圖。
  換成 Postgres 等其他資料庫時 `LIKE` 預設是 case-sensitive，行為就會不一致。TASKS.md 明確要求
  「case-insensitive」要用 SQLAlchemy filters 明確做到，所以要改成顯式寫法（`func.lower(col).contains(func.lower(q))`
  或 SQLAlchemy 的 `.ilike(f"%{q}%")`）。
- `backend/tests/test_notes.py` 目前只測完全比對子字串（`"Hello"` 對應内容含 `"Hello world"`），
  沒有測試「查詢字串大小寫跟資料庫實際內容大小寫不同」的情境（例如查 `"HELLO"` 或 `"hello"`）。
- `frontend/app.js` 完全沒有串接 `/notes/search/`——只有 `loadNotes()` 打 `/notes/`，沒有任何
  搜尋輸入框或呼叫 search endpoint 的程式碼。

## 要改哪些檔案、為什麼

| 檔案 | 改動 | 原因 |
|---|---|---|
| `backend/app/routers/notes.py` | `search_notes()` 裡把 `.contains(q)` 改成明確 case-insensitive 寫法（`ilike`或`func.lower`） | 讓「case-insensitive」是程式碼顯式意圖，不依賴資料庫預設 collation，符合TASKS.md要求且對日後換DB backend更穩健 |
| `backend/tests/test_notes.py` | 新增大小寫混合查詢的測試案例 | 現有測試沒覆蓋這個情境，補上才能驗證改動真的生效且防止回歸 |
| `frontend/app.js` | （待確認，見下） | TASKS.md #2 明確要求「Update frontend/app.js to use the search query」|

## 是否需要 schema 變更

**不需要。** 這個任務不涉及 `backend/app/models.py` 或 `backend/app/schemas.py` 的欄位新增/修改——
`NoteRead`/`NoteCreate` 的欄位都不變，`search_notes()` 的參數簽名（`q: str | None = None`）也不變。
因此本次規劃**不需要 db-agent** 進場。

## 對外部 API 行為的影響

- Endpoint path、method、query 參數名稱（`q`）、response schema（`list[NoteRead]`）都不變，
  對外部 API 契約沒有破壞性變更。
- 行為變化：在 SQLite 上，`ilike`/`lower()` 寫法的查詢結果應與現有 `.contains()` 結果**一致**
  （因為 SQLite LIKE 本來就對 ASCII case-insensitive），所以現有測試不會因此改動而變紅。
  真正的差異在於：換成 Postgres 等其他資料庫時，新寫法仍會保持 case-insensitive，舊寫法則不會——
  這屬於「讓現有隱含行為變成顯式、可移植」，不是使用者可見的破壞性變更。
- 沒有新增/刪除 query 參數，沒有變更 status code、沒有變更 error handling。

## 「顯式 case-insensitive」查詢邏輯歸屬 refactor-agent 還是 code-agent？

**判斷：歸屬 code-agent，不是 refactor-agent。**

理由：
- refactor-agent 的職責邊界明確定義為「結構套用」——Pydantic model 欄位、router 的回應/簽名
  結構，且其定義檔明文寫「不寫演算法邏輯（例如怎麼從文字裡解析出tag）」。
- 這次的改動不是新增/調整欄位或函式簽名，而是**改變查詢比對邏輯的語意**（從隱含依賴DB
  collation，改成明確在SQL層做大小寫正規化比對）——這是「業務邏輯裡的比對演算法決策」，
  跟 code-agent 定義檔裡「業務邏輯」的範疇（`services/*.py` 與 `routers/*.py` 裡業務邏輯呼叫的
  部分）吻合，尤其 code-agent 定義檔明確把 router 內的邏輯呼叫納入其職責範圍。
- 也沒有新欄位需要 db-agent 先提案，所以不會先經過 db-agent → refactor-agent 這條交棒鏈；
  本次直接是 code-agent 對現有 router 程式碼做業務邏輯調整。
- 因此本次工作流程較短：**code-agent（改查詢邏輯）→ test-agent（補大小寫測試 + 驗證全綠）→
  doc-agent（更新 API.md / TASKS_DONE.md）**，不需要 db-agent、refactor-agent 介入。

## 待確認：frontend UI 串接歸屬

TASKS.md #2 第二項要求「Update `frontend/app.js` to use the search query」，但這件事不落在
現有五個 backend 角色（db-agent / refactor-agent / code-agent / test-agent / doc-agent）任何一個
明確定義的職責範圍內——這五個 agent 的 `tools`/描述都聚焦在 `backend/`、`data/seed.sql`、
`backend/tests/`、文件檔，沒有一個提到 `frontend/`。

**待確認事項：**
1. 是否要讓 `code-agent` 擴大範疇涵蓋 `frontend/app.js`（目前其 description 明確寫「只改
   `backend/app/services/*.py`跟`routers/*.py`」，需要使用者明確放寬這個邊界定義才能這麼做）？
2. 或者 frontend UI 串接由使用者自己動手，不透過 agent 自動化？

在使用者明確回覆前，本規劃**不會**在 `tasks.md` 裡把 frontend 串接指派給任何現有 agent，
以免自行猜測職責邊界而讓「plan-agent 只規劃、不猜答案」的原則失效。
