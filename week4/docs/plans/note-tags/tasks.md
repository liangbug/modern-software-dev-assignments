# Tasks: Note tags 解析與儲存

對應 `design.md`。每項標明由哪個角色接手：`db-agent` / `refactor-agent` / `code-agent`。

## Schema / 儲存層（db-agent）

- [x] db-agent: 在 `backend/app/models.py` 的 `Note` 新增 `tags` 欄位，型別用 `sqlalchemy.JSON`，
      `nullable=False`、ORM `default=list`、DB `server_default="[]"`（依 `design.md` 的「Schema 變更」
      一節）
- [x] db-agent: 針對「已存在但沒有 `tags` 欄位的 `data/app.db`」決定並實作相容策略（`design.md` 裡標注
      的「待確認」二選一：輕量 `ALTER TABLE` migration guard，或明確記錄手動重建流程），並在程式碼/文件
      裡寫清楚選了哪個、為什麼 —— 選了選項2（文件記錄手動重建，不做自動 migration），理由見 db-agent
      交棒紀錄
- [x] db-agent: 同步更新 `data/seed.sql` 的 `CREATE TABLE notes (...)` 定義，補上 `tags` 欄位（含
      DB 層預設值），確保全新環境（`data/app.db` 不存在時）建出來的表跟 `models.py` 一致

## 解析邏輯（code-agent）

- [x] code-agent: 在 `backend/app/services/extract.py` 新增 `extract_tags(text: str) -> list[str]`，
      依 `design.md` 的「`extract_tags` 解析規則」實作（正規表達式抓 `#tag`、小寫正規化、依首次出現順序
      去重、無合法 tag 回傳 `[]`）
- [x] code-agent: 在 `backend/tests/test_extract.py` 新增 `extract_tags` 的單元測試，覆蓋
      `testing.md` 裡對應的情境（多個 tag、重複 tag、大小寫、無 tag、`#` 後面無合法字元）

## API 串接（實際執行時由 refactor-agent 做 schema、code-agent 做 router 串接 —— 見下方備註）

- [x] refactor-agent: 在 `backend/app/schemas.py` 的 `NoteRead` 新增 `tags: list[str]` 欄位（預設 `[]`）；
      `NoteCreate` 維持不變（不開放使用者直接傳 `tags`，理由見 `design.md`）
- [x] code-agent: 在 `backend/app/routers/notes.py` 的 `create_note`：呼叫
      `extract_tags(payload.content)`，把結果指定給新建的 `Note` 物件的 `tags`，`flush`/`refresh` 後
      回傳的 `NoteRead` 要能看到 `tags`
- [x] code-agent: 在 `backend/tests/test_notes.py` 新增/擴充整合測試，驗證 `POST /notes/` 用含
      `#tag` 的 content 建立 note 後，回應 JSON 的 `tags` 欄位符合預期（對應 `testing.md` 的情境）

> 備註（doc-agent 收尾檢查時發現並修正的落差）：原始版本把「`schemas.py` 的 `NoteRead` 加 `tags`」指派
> 給 code-agent，跟 `refactor-agent.md` 自己宣告的職責（Pydantic schema 結構套用）衝突。實際執行時是
> 依 `refactor-agent.md` 的既定邊界，改由 refactor-agent 完成這項，上面已修正指派歸屬。六個 agent 定義檔
> 已同步修正（plan-agent 現在會先讀其他角色的職責邊界再拆任務，避免下次再指派錯）。

## 收尾檢查（refactor-agent）

- [x] refactor-agent: 檢查 `extract.py` 新增 `extract_tags` 後，跟既有 `extract_action_items` 是否
      職責清楚分離、命名/回傳型別一致（都回傳 `list[str]`），若解析用的正規表達式/常數有重複可抽出共用
      helper；確認不影響 `extract_action_items` 既有行為
- [x] refactor-agent: 確認改動後 `make format && make lint` 能過（黑名單：不要為了過 lint 改變
      `extract_tags`/`extract_action_items` 的對外行為）

## 交棒提醒

db-agent 應先讀 `design.md`「Schema 變更」一節開始；code-agent 的解析邏輯與 API 串接任務依賴
db-agent 先把 `tags` 欄位建好（否則 `routers/notes.py` 沒有欄位可寫）；refactor-agent 排在最後做收尾
檢查。測試情境詳見 `testing.md`。
