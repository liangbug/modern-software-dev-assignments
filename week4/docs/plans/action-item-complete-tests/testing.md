# Testing: Complete action item flow — 補測試覆蓋

Given/When/Then 情境，對應 `tasks.md`。

## 情境一：PUT不存在的id

- Given: 資料庫中不存在`id=999999`（或其他確定不存在）的action item
- When: 呼叫 `PUT /action-items/999999/complete`
- Then: 回應狀態碼 `404`，回應 body 的 `detail` 為 `"Action item not found"`（對照
  `backend/app/routers/action_items.py` 現有的 `HTTPException(status_code=404, ...)`）

## 情境二：重複PUT同一個已complete的item（主線／選項A：現況即預期）

- Given: 先 `POST /action-items/` 建立一個item，再 `PUT /action-items/{id}/complete` 一次，確認第一次
  回應`completed`為`true`
- When: 對**同一個id**再呼叫一次 `PUT /action-items/{id}/complete`
- Then: 第二次呼叫仍回應狀態碼 `200`，body 的 `completed` 仍為 `true`（沒有報錯，行為idempotent），
  且不應出現例外或500

## 情境二之替代版本（僅選項B成立、決定改為報錯時才採用，與上面情境二二選一，不同時存在於測試檔中）

- Given: 同上，先建立並complete一次某item
- When: 對同一個id再呼叫一次 `PUT /action-items/{id}/complete`
- Then: 第二次呼叫回應狀態碼 `409`（或協議定案的status code），body 帶有明確訊息（例如
  `"Action item already completed"`），且該item的`completed`欄位不因這次呼叫而改變（維持原本的
  `true`，可用後續`GET /action-items/`確認未被破壞）

## 情境三（可選，補強coverage）：complete後透過list確認持久化

- Given: 建立一個item並complete
- When: 呼叫 `GET /action-items/`
- Then: 回應中該item的`completed`為`true`，驗證完成狀態確實寫入DB而非只在單次回應中呈現（現有
  `test_create_and_complete_action_item`已部分覆蓋此情境，若既有測試已足夠可不必重複新增）
