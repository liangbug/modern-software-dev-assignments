# Tasks: Request validation and error handling

依 `design.md` 的職責邊界拆分。標記「(條件性)」的項目需先由使用者確認 `design.md` 裡對應的「待確認」
編號後才能開工,不要在確認前預先實作其中一個猜測答案。

- [x] refactor-agent: 在 `backend/app/schemas.py` 的 `NoteCreate.title`、`NoteCreate.content`、
      `ActionItemCreate.description` 加上 `Field(min_length=1)`,禁止空字串。
      (實作採 `field_validator` + `strip()` 檢查,一併涵蓋待確認②,而非單純 `min_length=1`。)
- [x] refactor-agent: (條件性,待確認②) 使用者確認也要擋「全空白字串」,已在 `NoteCreate`、
      `NoteUpdate`、`ActionItemCreate` 對應欄位加上 `not_blank` validator(`v.strip()` 為空即拒絕)。
      `NoteUpdate` 的 `title`/`content` 為 `Optional`,`None` 時允許通過(代表不更新),有帶值時才檢查。
- [x] refactor-agent: (條件性,待確認③) 使用者確認驗證失敗維持 FastAPI 預設 422,不加自訂 exception
      handler,`backend/app/main.py` 未變更。
- [x] test-agent: 在 `backend/tests/test_notes.py` 新增測試:`POST /notes/`、`PUT /notes/{id}` 傳入空
      字串或純空白字串 `title`/`content` 應回 422,不建立/不更新資料。
- [x] test-agent: 在 `backend/tests/test_action_items.py` 新增測試:`POST /action-items/` 傳入空字串或
      純空白字串 `description` 應回 422。
- [x] test-agent: 在 `backend/tests/test_notes.py` 新增測試,確認 `GET /notes/{不存在的id}` 回 404(現況
      已正確,補上測試覆蓋即可,不需改程式)。`PUT/DELETE /notes/{不存在id}` 回 404 的測試已由 task5
      (note CRUD enhancements)覆蓋(`test_update_note_missing_id_returns_404`、
      `test_delete_note_missing_id_returns_404`),不重複補。
- [x] test-agent: 在 `backend/tests/test_action_items.py` 新增測試,確認 `PUT /action-items/{不存在的id}
      /complete` 回 404(現況已正確,補上測試覆蓋即可,不需改程式)。
- [x] (待確認①) 使用者確認本次 404 測試範圍納入 notes 的 `PUT/DELETE /notes/{id}`——這兩個 endpoint
      已由 task5 實作完成並附帶 404 測試,本次任務不需再補新增,已於上一項標註引用既有測試。
- [x] doc-agent: 測試全綠後,把本次變更(schemas.py 的長度限制、驗證失敗狀態碼、既有 404 行為的測試
      覆蓋)記錄進 `docs/TASKS_DONE.md`,對應 `docs/TASKS.md` 第 6 項。
