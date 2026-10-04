# Testing scenarios: Add search endpoint for notes (docs/TASKS.md #2)

對應 `tasks.md` 裡 code-agent / test-agent 的項目，至少各有一個情境覆蓋。

## 情境 1：大小寫混合查詢應命中大小寫不同的內容（對應 code-agent 修改查詢邏輯 + test-agent 新增測試）

- Given：已建立一筆 note，`title="Trip"`, `content="Plan a Trip to Tokyo"`
- When：呼叫 `GET /notes/search/?q=TOKYO`（查詢字串全大寫，跟內容裡的 `"Tokyo"` 大小寫不同）
- Then：回應 status code 200，回傳的 notes 清單裡包含剛建立的那筆 note

## 情境 2：查詢字串小寫、內容為大寫開頭，同樣應命中（對應同一項 code-agent/test-agent 任務，補齊另一方向）

- Given：已建立一筆 note，`title="URGENT Reminder"`, `content="please follow up soon"`
- When：呼叫 `GET /notes/search/?q=urgent`（全小寫查詢）
- Then：回應 status code 200，回傳的 notes 清單裡包含剛建立的那筆 note（因為 title 含
  `"URGENT"`，比對應忽略大小寫）

## 情境 3：現有子字串查詢行為不回歸（對應 code-agent 跑 make test 確認既有測試不受影響）

- Given：已建立一筆 note，`title="Test"`, `content="Hello world"`（沿用現有
  `test_create_and_list_notes` 的資料）
- When：呼叫 `GET /notes/search/?q=Hello`（跟現有測試相同的查詢字串與大小寫）
- Then：回應 status code 200，且回傳清單長度 `>= 1`，跟改動前的既有測試斷言一致（不應變紅）

## 情境 4：空/未帶查詢字串仍回傳全部 notes（對應 test-agent 全量驗證，確保沒有破壞既有分支）

- Given：資料庫裡已存在至少一筆 note
- When：呼叫 `GET /notes/search/`（不帶 `q` 參數）
- Then：回應 status code 200，回傳清單筆數與 `GET /notes/`（列出全部 notes）一致

## 情境 5：文件更新後與實際行為一致（對應 doc-agent 更新 API.md / TASKS_DONE.md）

- Given：`docs/API.md` 已依本次改動更新 `GET /notes/search/?q=` 的說明，註明其為
  case-insensitive
- When：對照 `/openapi.json` 或直接讀 `backend/app/routers/notes.py` 目前的 `search_notes()`
  實作
- Then：`API.md` 描述的參數、回應 schema、行為說明（case-insensitive）與實際程式碼一致，
  且 `docs/TASKS_DONE.md` 有記錄 TASKS.md #2 已完成，`docs/TASKS.md` 本身內容未被修改
