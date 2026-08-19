# Tasks Done

`docs/TASKS.md` 本身不異動(維持原始任務描述),完成狀態跟細節記錄在這裡。每筆對應 `TASKS.md` 的項目編號。

## 4) Improve extraction logic

- **Extend `backend/app/services/extract.py` to parse tags like `#tag` and return them** — done.
  Added `extract_tags(text)`(regex `#(\w+)`,小寫正規化,依首次出現順序去重);串接進
  `POST /notes/`(`routers/notes.py`)讓 `Note.tags` 在建立時被填入,`NoteRead.tags`(`schemas.py`)
  在 list/create/search/get 回應都帶出。
- **Add tests for the new parsing behavior** — done. `backend/tests/test_extract.py` 新增 5 個
  `extract_tags` 單元測試;`backend/tests/test_notes.py` 新增 3 個整合測試
  (`test_create_note_with_hashtags_returns_parsed_tags`、
  `test_create_note_without_hashtags_returns_empty_tags`、
  `test_get_note_returns_persisted_tags`)。全套 11 個測試通過,lint 乾淨。
- **(Optional) Expose `POST /notes/{id}/extract` that turns notes into action items** — 未做,不在本次
  規劃範圍內(見 `docs/plans/note-tags/design.md`)。

跑這次自動化的過程記錄在 `docs/plans/note-tags/{design.md,tasks.md,testing.md}`,由六個
SubAgent(`plan-agent → db-agent → refactor-agent → test-agent → code-agent → test-agent → doc-agent`)
接力完成。
