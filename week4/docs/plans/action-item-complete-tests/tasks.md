# Tasks: Complete action item flow — 補測試覆蓋

對應 `design.md`。每項標明由哪個角色接手。

## 主線（選項A：現況即預期，只補測試——預設路徑）

- [x] test-agent: 在 `backend/tests/test_action_items.py` 新增測試，涵蓋「PUT不存在的id」情境，斷言
      `404` + `detail: "Action item not found"`（對應 `testing.md` 情境一）
- [x] test-agent: 在 `backend/tests/test_action_items.py` 新增測試，涵蓋「重複PUT同一個已complete的
      item」情境，斷言仍回 `200`、`completed` 仍為 `true`（釘住現況idempotent行為，對應 `testing.md`
      情境二）
- [x] test-agent: 跑 `make test` 確認新增測試全部通過（此路徑下不應有紅測試，因為現況程式碼已滿足
      斷言）
- [x] doc-agent: 在 `docs/TASKS_DONE.md` 記錄第3項「Complete action item flow」完成狀態，說明補了
      404跟重複complete兩個測試情境；因為沒有API行為變更，`docs/API.md`不需要新增內容（如果
      `docs/API.md`本身還沒有 `/action-items/{id}/complete` 這條說明，順手補上現況行為描述）

## 條件分支（選項B：若使用者/後續決定「重複complete應報錯」才執行下面這條路徑，不與選項A同時做）

- [ ] （待確認後才執行）test-agent: 先把「重複PUT同一個已complete的item」測試改寫成斷言
      `409`（或協議好的status code）+ 明確detail訊息，此時應為紅測試
- [ ] （待確認後才執行）code-agent: 在 `backend/app/routers/action_items.py` 的 `complete_item` 加上
      `if item.completed: raise HTTPException(...)` 判斷，讓上面的紅測試轉綠；不改動404那段既有邏輯
- [ ] （待確認後才執行）test-agent: 跑 `make test` 驗證新判斷沒有連帶弄壞其他既有測試（尤其原本的
      `test_create_and_complete_action_item`，其中"第一次complete"仍應成功回200）
- [ ] （待確認後才執行）doc-agent: 在 `docs/API.md` 補充 `PUT /action-items/{id}/complete` 對「已完成
      item再次呼叫」回409的行為說明，並在 `docs/TASKS_DONE.md` 記錄

## 收尾

- [x] doc-agent: 檢查本檔案checkbox是否有遺漏未勾的項目，回報哪些角色該勾卻沒勾。結果：選項B的4項
      （test-agent x2、code-agent x1、doc-agent x1）維持未勾——按設計是「待確認後才執行」的條件分支，
      本次未執行409行為變更，故不勾選，非遺漏。
