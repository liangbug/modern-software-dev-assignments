# Design: Notes CRUD enhancements

對照 `docs/TASKS.md` 第5項:

> 5) Notes CRUD enhancements
> - Add `PUT /notes/{id}` to edit a note (title/content)
> - Add `DELETE /notes/{id}` to delete a note
> - Update `frontend/app.js` to support edit/delete; add tests

## 1. 現況(讀code得到的事實)

- `backend/app/models.py`:`Note`(id/title/content/tags,JSON欄位)跟`ActionItem`(id/description/
  completed)是兩個**互相獨立**的table,**沒有任何`ForeignKey`或`relationship()`把兩者關聯起來**。
  目前程式碼裡完全找不到`note_id`這種欄位。
- `backend/app/schemas.py`:只有`NoteCreate`(title/content,兩者都必填)跟`NoteRead`(id/title/
  content/tags)。沒有`NoteUpdate`。
- `backend/app/routers/notes.py`:目前只有`GET /notes/`、`POST /notes/`、`GET /notes/search/`、
  `GET /notes/{note_id}`。沒有`PUT`/`DELETE`。`get_note`已有404 pattern可參考:
  `HTTPException(status_code=404, detail="Note not found")`。
- `frontend/app.js`:`loadNotes()`只把每個note渲染成`<li>${title}: ${content}</li>`,沒有任何
  edit/delete相關的DOM元素、按鈕或fetch呼叫。

## 2. PUT /notes/{id} 設計

**採用部分更新(PATCH語意但走PUT路徑,因為TASKS.md明確要求`PUT`)**:新增`NoteUpdate` pydantic model,
`title: str | None = None`、`content: str | None = None`,兩者都optional。Router裡只更新有帶值的欄位,
其餘欄位維持原值。理由:

- 若要求「整份取代」,前端每次PUT都要先GET一次拿到完整內容再送出,對「只改標題」這種常見情境不必要地
  笨重。
- 現有`NoteCreate`兩欄位都必填,是「新建」語意;`NoteUpdate`若也要求兩欄位必填,等於跟`NoteCreate`重複,
  沒有表達出「部分修改」的彈性,也跟一般REST PUT/PATCH慣例對讀者的直覺(允許只送要改的欄位)不符。

回應:`response_model=NoteRead`,回傳更新後的完整note(跟`POST /notes/`一致的慣例)。

### 待確認 A:PUT時若`content`有變更,`tags`要不要重新用`extract_tags()`解析?

`docs/TASKS.md`第4項(已完成)讓`POST /notes/`在建立時呼叫`extract_tags(payload.content)`存入`tags`。
但第5項的任務描述完全沒提到PUT跟tags的關係。若「編輯content卻不重新解析tags」,會讓`tags`跟目前`content`
不同步(舊tags留著、新增的`#tag`不會被抓到),這跟使用者直覺(tags應該反映目前content)可能矛盾。但
task描述裡`PUT /notes/{id}`只寫「編輯title/content」,沒提tags,所以**不確定**是否要在PUT時把tags納入
處理範圍。這裡不自行假設答案,留給實作前確認:
- 選項1:PUT時若content有變更,重新呼叫`extract_tags`覆蓋`tags`(維持tags跟content同步)。
- 選項2:PUT完全不動tags欄位(嚴格照任務字面「只編輯title/content」)。

## 3. DELETE /notes/{id} 設計

### 關聯action_items的處理

**依現有`models.py`的事實:`Note`跟`ActionItem`之間沒有`ForeignKey`、沒有`relationship()`,兩個table
互不關聯。** 因此刪除一個note,**不會**觸發任何cascade行為,也不需要在router裡額外處理action_items的
刪除或更新——目前資料模型下,DELETE /notes/{id}就是單純刪掉`notes`表的一列,對`action_items`表沒有任何
影響(無論是否設計cascade,因為根本沒有關聯欄位可以cascade)。

這點在`testing.md`裡仍列一個情境驗證(刪除note後,既有action_items數量/內容不變),避免未來有人誤以為
兩者有關聯而寫出錯誤的cascade邏輯。

### 待確認 B:DELETE的成功回應要回傳什麼?

REST慣例上DELETE成功常見兩種做法:
- `204 No Content`,body為空(較嚴格的REST慣例)。
- `200 OK`,回傳被刪除的note物件(方便前端不用另外快取就能顯示「已刪除OO」的訊息)。

`docs/TASKS.md`沒指定回應格式。這裡**沒有現成程式碼可以參照**(現有router都是回傳資料,沒有刪除
endpoint的先例),建議採用`204 No Content`(FastAPI標準做法,`status_code=204`且不回傳body),但正式
拍板前列為待確認,因為若前端需要用回傳值更新畫面(例如顯示「OO已刪除」的title),可能會偏好`200`帶
被刪除note的內容。

### 404處理規範

跟`get_note`一致:找不到note時`raise HTTPException(status_code=404, detail="Note not found")`。
PUT、DELETE都套用同一規範(先`db.get(Note, note_id)`確認存在,不存在就404,存在才繼續update/delete)。

## 4. 對外部API的影響

- 新增兩個endpoint,不影響既有`GET /notes/`、`POST /notes/`、`GET /notes/search/`、`GET /notes/{id}`
  的既有行為跟回應格式。
- `NoteRead`不需要改動(PUT沿用既有回應格式)。
- 新增`NoteUpdate`是全新的request model,不影響`NoteCreate`。
- 是否需要schema變更(DB層):**不需要**。`Note`/`ActionItem`的欄位定義完全不用改,`data/seed.sql`也不用
  跟著調整——這次任務純粹是新增router endpoint + Pydantic request model,不涉及`models.py`欄位新增。

## 5. 待確認 C:frontend編輯/刪除UI該由誰做?

專案裡`.claude/agents/`的五個角色(`db-agent`/`refactor-agent`/`code-agent`/`test-agent`/`doc-agent`)
的職責描述裡,提到的檔案範圍都是`backend/app/`、`backend/tests/`、`data/`、`docs/`——**沒有任何一個角色
的「職責」段落提到`frontend/`或`frontend/app.js`**。也就是說,`frontend/app.js`的編輯/刪除UI不落在既定
的五角色backend流程職責邊界內。這裡不擅自把它塞給`code-agent`或`refactor-agent`(那會混淆「backend業務
邏輯」跟「前端UI」的邊界),**標注待確認**:需要使用者/後續流程決定由誰(可能是額外的frontend-agent,或
由使用者手動處理)完成`frontend/app.js`裡「編輯/刪除按鈕 + fetch PUT/DELETE呼叫」這部分,`tasks.md`裡
會把這一項列出來但標明「角色待確認」而不是塞進既有五角色之一。
