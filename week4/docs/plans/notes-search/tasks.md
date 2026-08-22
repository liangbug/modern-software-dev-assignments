# Tasks: Add search endpoint for notes (docs/TASKS.md #2)

- [x] code-agent: 修改 `backend/app/routers/notes.py` 的 `search_notes()`，把
      `Note.title.contains(q) | Note.content.contains(q)` 改成顯式 case-insensitive 寫法
      （例如 `Note.title.ilike(f"%{q}%") | Note.content.ilike(f"%{q}%")`，或用
      `func.lower(Note.title).contains(func.lower(q))`），不改變 endpoint 簽名、路徑、回應 schema。
- [x] code-agent: 跑 `make test` 確認既有測試（`test_create_and_list_notes` 等）不受影響仍全綠，
      再跑 `make format && make lint` 收尾。
- [x] test-agent: 在 `backend/tests/test_notes.py` 新增大小寫混合查詢的測試（見 `testing.md`），
      涵蓋「建立時用某種大小寫，查詢時用不同大小寫」的情境。
- [x] test-agent: 跑 `make test` 驗證新測試與既有測試全數通過，回報 pass/fail 結果。
- [x] doc-agent: 更新 `docs/API.md`（若不存在則建立），描述 `GET /notes/search/?q=` 的
      case-insensitive 行為與參數。
- [x] doc-agent: 在 `docs/TASKS_DONE.md` 記錄 TASKS.md #2（search endpoint 顯式 case-insensitive
      + 測試補齊）的完成狀態；**不編輯 `docs/TASKS.md` 本身**。
- [x] code-agent（使用者已核准擴大範疇）: `frontend/app.js` 串接 search UI（呼叫
      `/notes/search/?q=`、新增搜尋輸入框於 `frontend/index.html`，維持既有 `fetchJSON`/
      `loadNotes`/`loadActions` 命名慣例，新增 `searchNotes()`）。
