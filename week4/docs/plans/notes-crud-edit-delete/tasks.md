# Tasks: Notes CRUD enhancements

對應`design.md`。這次任務**不需要schema/model欄位變更**(見design.md第4節),所以沒有db-agent的項目。

- [x] refactor-agent: 在`backend/app/schemas.py`新增`NoteUpdate`(`title: str | None = None`、
      `content: str | None = None`,兩者optional),供PUT endpoint的request body使用。
- [x] refactor-agent: 在`backend/app/routers/notes.py`加上`PUT /notes/{note_id}`與
      `DELETE /notes/{note_id}`的endpoint簽名/裝饰器(`@router.put`/`@router.delete`,
      response_model依`design.md`第2、3節的決定),函式主體暫留TODO或最小stub,不寫實際的
      update/delete邏輯(那是code-agent的範圍)。
- [x] code-agent: 實作`PUT /notes/{note_id}`函式主體——`db.get(Note, note_id)`確認存在(不存在
      404,detail="Note not found"),依`NoteUpdate`裡有帶值的欄位更新`title`/`content`(部分更新,
      沒帶的欄位維持原值),`db.flush()`/`db.refresh()`後回傳`NoteRead`。已拍板:PUT時若content有
      更新,重新呼叫`extract_tags`覆蓋`tags`。
- [x] code-agent: 實作`DELETE /notes/{note_id}`函式主體——`db.get(Note, note_id)`確認存在(不存在
      404),存在則`db.delete(note)`並commit/flush。已拍板:回應`204 No Content`(無body)。不需處理
      `action_items`關聯(design.md已確認目前models.py無FK/relationship,無cascade需求)。
- [x] test-agent: 依`testing.md`裡每個given/when/then情境,在`backend/tests/test_notes.py`新增對應
      測試函式(PUT成功、PUT部分更新、PUT不存在id、DELETE成功、DELETE不存在id、DELETE後action_items
      不受影響)。
- [x] test-agent: 全部實作完成後跑`make test`驗證新舊測試都轉綠(20 passed),`make format && make
      lint`確認乾淨。
- [x] 角色待確認(已拍板由本次流程一併處理,範圍擴大): `frontend/app.js`、`frontend/index.html`裡
      新增編輯/刪除的UI(按鈕)與對應的`fetch('/notes/{id}', {method:'PUT'|'DELETE'})`呼叫。
