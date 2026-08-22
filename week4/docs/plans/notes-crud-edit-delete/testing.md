# Testing: Notes CRUD enhancements

以下情境對應`tasks.md`裡code-agent負責的`PUT`/`DELETE`實作。每個情境由test-agent轉成
`backend/tests/test_notes.py`裡的一個測試函式。

### 情境:PUT成功更新title跟content

- Given: 已存在一則note(先`POST /notes/`建立,取得`note_id`)
- When: 呼叫`PUT /notes/{note_id}`,body帶新的`title`跟`content`
- Then: 回應狀態碼200,回應的`NoteRead`裡`title`/`content`已更新成新值;再`GET /notes/{note_id}`確認
  持久化後的值跟PUT回應一致

### 情境:PUT只帶部分欄位(只更新title)

- Given: 已存在一則note,`title="Old"`、`content="Original content"`
- When: 呼叫`PUT /notes/{note_id}`,body只帶`{"title": "New"}`(不帶`content`)
- Then: 回應狀態碼200,`title`變成`"New"`,但`content`仍是`"Original content"`(未被清空或覆蓋成
  null)

### 情境:PUT不存在的id回404

- Given: 資料庫裡不存在id為`999999`的note(全新測試DB,不太可能自然存在此id)
- When: 呼叫`PUT /notes/999999`,body帶任意合法的`title`/`content`
- Then: 回應狀態碼404,回應body裡`detail`為`"Note not found"`

### 情境:DELETE成功刪除note

- Given: 已存在一則note(先`POST /notes/`建立,取得`note_id`)
- When: 呼叫`DELETE /notes/{note_id}`
- Then: 回應狀態碼依design.md「待確認B」拍板後的值(204或200);之後`GET /notes/{note_id}`回應404,
  且`GET /notes/`列表裡不再包含這個note_id

### 情境:DELETE不存在的id回404

- Given: 資料庫裡不存在id為`999999`的note
- When: 呼叫`DELETE /notes/999999`
- Then: 回應狀態碼404,回應body裡`detail`為`"Note not found"`

### 情境:DELETE note後,既有action_items不受影響

- Given: 已存在至少一則action item(先`POST /action-items/`建立,取得`action_item_id`),以及一則
  獨立的note(先`POST /notes/`建立,取得`note_id`)
- When: 呼叫`DELETE /notes/{note_id}`
- Then: 回應狀態碼符合刪除成功的定義;之後`GET /action-items/`裡該`action_item_id`仍存在、內容
  (`description`/`completed`)不變——驗證design.md裡「models.py無FK/relationship,無cascade」的
  結論在行為上成立
