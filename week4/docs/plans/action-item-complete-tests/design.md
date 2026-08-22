# Design: Complete action item flow — 補測試覆蓋

## 對照任務

`docs/TASKS.md` 第3項「Complete action item flow」：

> - Implement `PUT /action-items/{id}/complete`（already scaffolded）
> - Update UI to reflect completion（already wired）and extend test coverage

任務本身標明 endpoint 跟 UI 都已完成，唯一待辦是「extend test coverage」。本次規劃範圍鎖定在補測試，
不預設要改動 `backend/app/` 底下任何程式碼。

## 現況（讀碼結果）

- `backend/app/routers/action_items.py`：
  - `PUT /action-items/{item_id}/complete`（第27–36行）：
    ```python
    item = db.get(ActionItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Action item not found")
    item.completed = True
    db.add(item)
    db.flush()
    db.refresh(item)
    return ActionItemRead.model_validate(item)
    ```
  - **item不存在**：已有明確處理，回傳 `404` + `{"detail": "Action item not found"}`。
  - **重複complete（對已經`completed=True`的item再打一次`PUT .../complete`）**：程式碼沒有任何分支
    判斷「是否已完成」，會直接把`completed`重新設成`True`（本來就是`True`，等於no-op）、`flush`、
    `refresh`，回傳 `200` + 該item（`completed: true`）。**沒有報錯，也沒有任何提示「已經是完成狀態」**，
    是「靜默的、可重複呼叫的成功回應」（idempotent success）。
- `backend/tests/test_action_items.py`：目前只有 `test_create_and_complete_action_item` 一個
  happy-path測試，流程是create → complete（一次）→ list，斷言`completed`欄位跟 list 長度，完全沒有
  測試404或重複complete的case。
- UI（前端）方面：任務描述本身標記「already wired」，本次規劃不涉及前端程式碼改動，未讀
  `frontend/app.js`（不在補測試範圍內，若之後要驗證UI呈現需另開規劃）。

## 現況 vs. 預期行為：落差分析

### 1) Item不存在 → 404

**沒有落差**。現況已經是預期行為（回404、有明確detail訊息），純粹是**缺測試**，不需要code-agent動手，
只需要test-agent補上對應測試即可。

### 2) 重複complete同一個item

**待確認**：現況是「重複PUT回200、靜默no-op成功」，但`docs/TASKS.md`第3項本身**沒有明確定義**重複
complete該有的行為——沒有寫「應該回錯誤」還是「應該視為idempotent操作允許重複」。這是任務描述本身的
模糊之處，不是我（plan-agent）可以自行假設的：

- 若採**選項A（現況即為預期）**：重複complete視為合理的idempotent操作（PUT語意本來就允許重複呼叫
  產生相同結果），不需要改程式碼，只需要test-agent補一個測試，明確斷言「重複PUT仍回200、
  `completed`仍為`true`」，把現況行為釘住（regression-proof）。
- 若採**選項B（現況需要修正）**：重複complete應該回錯誤（例如`409 Conflict`或`400`，
  detail類似"Action item already completed"），讓呼叫方能區分「這是我第一次complete」跟
  「這個item早就complete過了」。這種情況下需要code-agent在`complete_item`裡加一段判斷
  `if item.completed: raise HTTPException(...)`，屬於業務邏輯變更，不是純補測試。

**本次規劃不代替使用者/開發者決定選項A或B**——因為兩者都是合理的API設計選擇，且`TASKS.md`原文沒有
給出線索。`tasks.md`會把兩條路徑都列出來，由執行者依決定選其中一條；若沒有明確指示，**預設先走
選項A（現況即預期，只補測試）**，因為這是風險最小、跟任務原文「extend test coverage」字面意思最
吻合的解讀；選項B的分支任務標記為「若採選項B才需要做」，不強制執行。

## 各角色分工邊界確認

讀過 `.claude/agents/{db-agent,refactor-agent,code-agent,test-agent,doc-agent}.md` 的「職責」段落後
確認：

- **db-agent**：只動`data/seed.sql`、`backend/app/models.py`欄位定義。本次任務不涉及schema變更
  （`ActionItem.completed`欄位早就存在），**不需要db-agent**。
- **refactor-agent**：只做Pydantic schema / router的「結構套用」（欄位、簽名），不寫業務邏輯。本次
  沒有新欄位、沒有結構變更，**不需要refactor-agent**。
- **code-agent**：只在測試需要「讓失敗測試轉綠」時，改`routers/*.py`裡的業務邏輯。**只有選項B成立
  時才需要code-agent**介入，在`complete_item`加上「已完成則報錯」的判斷；選項A（現況即預期）則完全
  不需要code-agent動手。
- **test-agent**：本次任務的主要角色。在`backend/tests/test_action_items.py`補上404、重複complete
  兩個情境的測試。若走選項A，測試應該一開始就是綠的（因為現況已經符合斷言）；若走選項B，測試要先寫
  成「預期409/400」的紅測試，等code-agent實作後才轉綠。
- **doc-agent**：測試全綠、行為定案後，若有API行為變更（僅選項B會有），需要在`docs/API.md`補上
  「重複complete回409」的說明；若走選項A（無行為變更），只需要在`docs/TASKS_DONE.md`記錄第3項完成
  狀態即可，不用動`docs/API.md`。

## 檔案改動範圍（本次規劃預期）

| 檔案 | 改動 | 負責角色 |
|---|---|---|
| `backend/tests/test_action_items.py` | 新增至少2個測試：PUT不存在的id → 404；重複PUT同一個已complete的item | test-agent |
| `backend/app/routers/action_items.py` | **僅選項B才需要**：`complete_item`加上已完成則報錯的判斷 | code-agent（條件性） |
| `docs/API.md` / `docs/TASKS_DONE.md` | 記錄本次完成狀態；若走選項B需補充「重複complete回409」的行為說明 | doc-agent |

## 待確認（給使用者/後續執行者）

1. **重複complete的預期行為**：idempotent允許（現況，回200）還是應該報錯（例如409）？本規劃預設先走
   「現況即預期」，只補測試釘住行為；若使用者/PM有不同意見，需要在執行`tasks.md`前先定案，因為這會
   決定要不要動用code-agent。
2. 前端`frontend/app.js`對「重複點擊complete按鈕」有沒有做disable或防呆處理，本次規劃未讀該檔案，
   若使用者需要一併確認UI行為，需另外擴大讀碼範圍。
