# Design: Note tags 解析與儲存

## 對照任務

`docs/TASKS.md` 第4項「Improve extraction logic」：

> - Extend `backend/app/services/extract.py` to parse tags like `#tag` and return them
> - Add tests for the new parsing behavior
> - (Optional) Expose `POST /notes/{id}/extract` that turns notes into action items

本次規劃範圍鎖定前兩條（tags 解析 + 測試），並補上使用者額外要求的「Note 新增 tags 欄位、把解析結果儲存
下來」。第三條（optional 的 action-item extract endpoint）**不在本次規劃範圍內**，因為它是把 note 轉成
action item 的既有功能延伸，跟 tags 欄位無直接關聯；若之後要做，建議另開一份獨立的 plan。

## 現況（讀碼結果）

- `backend/app/models.py`：`Note` 只有 `id/title/content`，沒有任何欄位存放解析結果。
- `backend/app/schemas.py`：`NoteCreate`/`NoteRead` 都只有 `title/content`。
- `backend/app/services/extract.py`：只有 `extract_action_items(text)`，逐行判斷 `TODO:`/`!` 結尾，
  沒有任何 tag 解析邏輯。
- `backend/app/routers/notes.py`：`create_note` 直接把 `payload.title/content` 存進 `Note`，沒有呼叫
  `extract.py` 裡任何函式；`list_notes`/`get_note`/`search_notes/` 都是原樣回傳 `NoteRead.model_validate(row)`。
- `backend/app/db.py` + `backend/app/main.py`：啟動時用 `Base.metadata.create_all(bind=engine)` 建表，
  **不會**對已存在的 SQLite 表做 `ALTER TABLE`；`apply_seed_if_needed()` 只在 `data/app.db` 這個檔案
  本身還不存在時，才套用 `data/seed.sql`（含自己的 `CREATE TABLE IF NOT EXISTS notes (...)`，欄位跟
  `models.py` 目前一致，都沒有 `tags`）。
- `backend/tests/test_extract.py`：目前只測 `extract_action_items`。
- `backend/tests/test_notes.py`：目前只測 create/list/search，沒有斷言任何欄位以外的內容。

## 要改哪些檔案、為什麼

| 檔案 | 改動 | 為什麼 |
|---|---|---|
| `backend/app/services/extract.py` | 新增 `extract_tags(text: str) -> list[str]`：用正規表達式抓 `#xxx` 形式的 token，正規化為小寫、依出現順序去重 | 任務要求的核心解析邏輯，跟既有 `extract_action_items` 平行存在，不互相影響 |
| `backend/app/models.py` | `Note` 新增 `tags` 欄位（型別見下） | 需要「儲存」解析結果，不能只在回應時算一次就丟掉 |
| `backend/app/schemas.py` | `NoteRead` 新增 `tags: list[str]`（預設 `[]`）；`NoteCreate` **不**新增 tags 欄位 | 對外回應要看得到 tags；tags 是從 content 解析出來的派生資料，不是使用者輸入，故不開放在 create payload 直接指定（見下方「待確認」） |
| `backend/app/routers/notes.py` | `create_note` 內：呼叫 `extract_tags(payload.content)`，把結果存進新建的 `Note.tags`，`db.flush()`/`refresh()` 後回傳 | 讓解析結果真正落到 DB，而不是只在回應時動態算 |
| `backend/app/db.py`（或等效位置） | 針對「已存在但沒有 `tags` 欄位的 `data/app.db`」補一段輕量 migration guard | 見下方「schema 變更」一節，避免舊 DB 檔案直接壞掉 |
| `data/seed.sql` | `CREATE TABLE notes (...)` 定義補上 `tags` 欄位（含預設值，例如 `TEXT NOT NULL DEFAULT '[]'`） | `apply_seed_if_needed()` 只在全新環境套用這份 SQL，若欄位定義沒同步，全新環境建出來的表跟 ORM 模型不一致 |
| `backend/tests/test_extract.py` | 新增針對 `extract_tags` 的單元測試 | 任務明確要求「Add tests for the new parsing behavior」 |
| `backend/tests/test_notes.py` | 新增/擴充針對 `POST /notes/` 回應含 `tags` 的整合測試 | 驗證「解析後有存到 DB、且 API 回應看得到」這條端到端行為 |

## Schema 變更

- **新增欄位**：`Note.tags`。
- **型別建議**：`sqlalchemy.JSON`（在 SQLite 底層以 TEXT 存 JSON 序列化字串，SQLAlchemy 存取時自動
  encode/decode 成 Python `list[str]`），比手刻逗號分隔字串更不容易踩到「tag 本身含逗號」之類的邊界情況。
- **預設值**：ORM 層 `default=list`（新建 Note 沒指定時是 `[]`），DB 層建議也給 `server_default`（例如
  `server_default="[]"`），這樣即使有人繞過 ORM 直接寫原生 SQL（像 `seed.sql`）插入 row 而沒帶 `tags`，
  也不會因為 `NOT NULL` 卻沒有預設值而失敗。
- **nullable**：建議 `nullable=False`（永遠是列表，最差是空列表，不用讓呼叫端多判斷 `None`）。
- **對既有 `data/app.db` 的相容性影響（重要）**：
  - `Base.metadata.create_all(bind=engine)` **只會建立不存在的表，不會對已存在的表做 `ALTER TABLE`**。
  - 目前 repo 裡如果本機已經跑過 `make run`/`make seed` 產生過 `data/app.db`，這個檔案裡的 `notes` 表
    是舊結構（沒有 `tags` 欄位）。改完 `models.py` 之後，**下次啟動 app 或跑測試 fixture 用到這個舊檔案
    時，任何 SELECT/INSERT 涉及 `tags` 欄位都會噴 `OperationalError: no such column: notes.tags`**。
  - `backend/tests/conftest.py` 的 `client` fixture 用的是暫存 DB（每次測試重新建表），所以測試本身不受
    這個問題影響；但**本機手動跑 `make run` 用的是真正的 `data/app.db`，會踩到**。
  - 因此本次設計要求 db-agent 額外處理其中一種相容策略（二選一，需在實作時定案，目前先在此標注
    「待確認」——由 db-agent 依 repo 慣例決定哪個更合適）：
    1. 在 `db.py` 啟動流程裡加一段輕量 guard：用 `PRAGMA table_info(notes)` 檢查 `tags` 欄位是否存在，
       不存在就執行一次 `ALTER TABLE notes ADD COLUMN tags TEXT NOT NULL DEFAULT '[]'`。
    2. 明確記錄「這是 dev/教學用 repo，改 schema 後請刪除本機 `data/app.db` 重新 `make seed`」，不做
       自動 migration。
  - **待確認**：repo 定位是教學作業（`CLAUDE.md` 明確說「避免動 `data/app.db`」「測試永遠用暫存
    DB」），沒有 Alembic 之類的 migration 工具，也沒有前例處理過欄位新增。选項1 更穩但增加 `db.py`
    複雜度；選項2 更簡單但要求開發者手動介入。這點由 db-agent 決定並在其任務裡寫清楚選了哪個、為什麼。

## 對外部行為（API 回應格式）的影響

- `GET /notes/`、`GET /notes/{id}`、`GET /notes/search/`、`POST /notes/`：回應 JSON 都會多一個
  `"tags": [...]` 欄位。這是**新增欄位、非破壞性變更**（既有 client 若忽略未知欄位不受影響；若有嚴格
  schema 驗證的 client 才會受影響，目前前端 `frontend/app.js` 沒有這類嚴格驗證）。
- **待確認/範圍限制**：本次只在 `create_note`（`POST /notes/`）時計算並存入 `tags`。
  - 既有（seed 產生或改動前建立）的 note，`tags` 會是空列表，直到有人重新建立或（若未來實作）編輯時
    重新解析——**本次不處理「編輯 note 時要不要重新解析 tags」**，因為 `PUT /notes/{id}` 是
    `docs/TASKS.md` 第5項的範圍，不在本任務內。若之後第5項實作了編輯功能，需要另外決定「編輯 content
    時是否重算 tags」，屆時建議回頭補一份小規劃或在第5項的規劃裡帶到。
  - `NoteCreate` 是否要開放使用者直接指定 `tags`（而不是只能從 content 解析）：本次設計傾向不開放
    （tags 應該是 content 的派生資料，避免「使用者填的 tags」跟「content 裡的 #tag」不同步、造成混
    淆）。如果之後有需求要讓使用者手動覆寫/補充 tags，需要重新規劃 schema（例如區分 `auto_tags` 和
    `manual_tags`），本次不預先做這個擴充。

## `extract_tags` 解析規則（供 code-agent 實作參考）

- 用正規表達式抓 `#` 後面接的 word 字元（字母/數字/底線，或視需求加 `-`），例如 `#urgent`、`#follow_up`。
- 正規化：全部轉小寫（避免 `#Urgent` 跟 `#urgent` 被當成兩個不同 tag）。
- 去重但保留「第一次出現」的順序（跟 `testing.md` 裡的情境對齊）。
- 邊界情況（testing.md 會列對應情境）：content 沒有任何 `#tag` → 回傳 `[]`；同一個 tag 出現多次 → 只出現
  一次；`#` 後面沒有任何合法字元（例如單獨一個 `#` 或 `# space`）→ 不算一個 tag。
