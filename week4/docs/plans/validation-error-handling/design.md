# Design: Request validation and error handling

對應 `docs/TASKS.md` 第 6 項:

> Add simple validation rules (e.g., min lengths) to `schemas.py`
> Return informative 400/404 errors where appropriate; add tests for validation failures

## 1. 現況盤點

### 1.1 `backend/app/schemas.py`

```python
class NoteCreate(BaseModel):
    title: str
    content: str

class ActionItemCreate(BaseModel):
    description: str
```

沒有任何 `Field(min_length=...)` 或自訂 validator。`title`/`content`/`description` 目前都接受空字串 `""`,
因為 pydantic 對 `str` 型別預設只檢查型別,不檢查長度。

### 1.2 `backend/app/routers/notes.py` 現況

- `GET /notes/` — 無驗證需求(無 path/body 參數)。
- `POST /notes/` — 吃 `NoteCreate`,無長度限制,空字串會被接受並成功建立(201)。
- `GET /notes/search/` — `q` 是 optional query string,無驗證需求。
- `GET /notes/{note_id}` — **已經**用 `HTTPException(404, "Note not found")` 處理不存在的情況,行為正確。
- **沒有 `PUT /notes/{id}`、`DELETE /notes/{id}`** — 這兩個 endpoint 屬於 `docs/TASKS.md` 第 5 項
  (Notes CRUD enhancements),目前程式碼裡不存在,不是本次任務(第 6 項)範圍內建立的。

### 1.3 `backend/app/routers/action_items.py` 現況

- `POST /action-items/` — 吃 `ActionItemCreate`,無長度限制,空字串會被接受。
- `PUT /action-items/{item_id}/complete` — **已經**用 `HTTPException(404, "Action item not found")`
  處理不存在的情況,行為正確。
- **沒有 `GET /action-items/{id}`、`PUT /action-items/{id}`、`DELETE /action-items/{id}`** —
  這些單一資源的 get/update/delete endpoint 目前程式碼裡完全不存在。

### 1.4 結論:現況「不存在資源時的錯誤」是否已處理?

已存在的兩個「操作單一資源」的 endpoint(`GET /notes/{id}`、`PUT /action-items/{id}/complete`)**都已經**
正確回 404,不是 500 或其他錯誤。目前程式碼裡**沒有**任何地方會在資源不存在時噴出未處理的 500。

**待確認①**:任務描述「更新/刪除/complete 不存在資源的 404 案例」暗示 notes 有 update/delete、action
items 有更多單一資源操作,但這些 endpoint 在目前程式碼裡並不存在(屬於第 5 項任務範圍,尚未開工,見
`week4/CLAUDE.md`「目前狀態」)。本次任務(第 6 項)的範圍應限定在:
  (a) 只驗證/測試「目前已存在」的 endpoint(`GET /notes/{id}`、`PUT /action-items/{id}/complete`)的
      404 行為,還是
  (b) 連帶把第 5 項的 `PUT/DELETE /notes/{id}` 一併做出來,才能有東西可以測「更新/刪除不存在的 note 回
      404」?
  在使用者/後續角色確認前,`tasks.md`、`testing.md` 只會覆蓋現況(a),並把 (b) 標記為需要先完成第 5 項
  依賴,不在此規劃裡預先假設答案。

## 2. 驗證規則設計(`schemas.py`)

目標欄位:`NoteCreate.title`、`NoteCreate.content`、`ActionItemCreate.description`。

提案:

```python
from pydantic import BaseModel, Field

class NoteCreate(BaseModel):
    title: str = Field(min_length=1)
    content: str = Field(min_length=1)

class ActionItemCreate(BaseModel):
    description: str = Field(min_length=1)
```

- `min_length=1`:禁止空字串 `""`。這是 `docs/TASKS.md` 字面提到的「min lengths」,對應最小改動。
- 不設 `max_length` 上限,因為任務描述沒提到上限需求,不擅自加。

**待確認②**:`min_length=1` 只擋得住完全空字串 `""`,擋不住全空白字串(例如 `"   "`,長度不是 0)。
是否也要禁止「全空白視為空」?若要,需要額外的 validator(例如 `str.strip()` 後檢查長度,或
pydantic v2 的 `Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]`),這已經超出
「min length」字面範圍一點,屬於延伸判斷。在使用者確認之前,本規劃**先只做 `min_length=1`(擋純空字串)**,
全空白字串的檢查列為待確認、暫不納入 `tasks.md` 的必做項,由後續角色實作時視確認結果決定是否加做。

## 3. 驗證失敗要回 400 還是 422?

- pydantic/FastAPI 對 request body 驗證失敗的**預設行為**是回 `422 Unprocessable Entity`,不是 400。
  這是 FastAPI 內建的 `RequestValidationError` handler 行為,不需要任何額外程式碼就會發生。
- `docs/TASKS.md` 寫的是「400/404」,字面上暗示驗證失敗要回 400。若要把驗證失敗從預設的 422 改成 400,
  作法是在 `backend/app/main.py` 加一個自訂 exception handler:

  ```python
  from fastapi import Request
  from fastapi.exceptions import RequestValidationError
  from fastapi.responses import JSONResponse

  @app.exception_handler(RequestValidationError)
  def validation_exception_handler(request: Request, exc: RequestValidationError):
      return JSONResponse(status_code=400, content={"detail": exc.errors()})
  ```

  這會把**所有** endpoint 的 422 改成 400,是全域行為改動,不是只影響 `NoteCreate`/`ActionItemCreate`。

**待確認③**:是否真的要把 422 改成 400,還是「有驗證(不管回 400 或 422)就算完成本任務」?
- 若使用者原意其實是「只要驗證失敗有明確錯誤訊息就好,422 也算數」,則**不需要**在 `main.py` 加自訂
  exception handler,`tasks.md` 就不會有這一項,`testing.md` 的驗證失敗情境會斷言 `422`。
- 若使用者堅持要 400,則需要新增上面的 exception handler(影響範圍是全域 `main.py`,不只是
  `schemas.py`),`testing.md` 的驗證失敗情境會斷言 `400`。

在使用者確認前,`tasks.md` 把「加自訂 exception handler 讓驗證失敗回 400」列為**條件性任務**並在項目
文字裡註明「若確認要 400 才做,否則維持 FastAPI 預設 422」,避免直接假設其中一個答案。

## 4. 影響到的檔案

- `backend/app/schemas.py` — 加 `Field(min_length=1)`(結構性變更,屬於 `refactor-agent` 職責範圍,
  因為這是 Pydantic model 的欄位定義,不是業務邏輯)。
- `backend/app/main.py` — **只有在待確認③確認要 400 時才需要改**,加全域 exception handler。這是
  跨 endpoint 的行為改動,不屬於任何單一 router 的業務邏輯,也不是 schema 欄位定義本身;在職責邊界上
  比較接近 `refactor-agent`(結構/框架層設定),而不是 `code-agent`(單一 service/router 的業務邏輯)。
  這點在後續指派 `tasks.md` 時已依此判斷,若後續角色認為應歸 `code-agent`,請在該步驟回報說明理由。
- `backend/tests/test_notes.py`、`backend/tests/test_action_items.py` — 新增驗證失敗與 404 測試
  (`test-agent` 職責)。
- 不需要 schema/model 欄位新增,**不需要 db-agent 介入**——這次任務沒有新增資料庫欄位,只是對既有
  `str` 欄位加長度限制,`models.py`、`data/seed.sql` 都不受影響(seed 資料裡的 title/content/description
  本來就非空,不會被新規則擋下)。

## 5. 對外部行為(API 回應格式)的影響

- `POST /notes/`、`POST /action-items/` 傳入空字串 `title`/`content`/`description` 時,回應會從
  「201 成功建立空白資料」變成「422(或依待確認③結果為 400)驗證錯誤,不建立資料」。這是刻意的行為改變,
  frontend(`frontend/app.js`)若有相應的空值送出情境,可能需要同步處理錯誤回應,但這次任務不包含前端
  改動(`docs/TASKS.md` 第 6 項只提到 `schemas.py` 跟錯誤處理,沒提到 frontend)。
- 既有的 `GET /notes/{note_id}`、`PUT /action-items/{item_id}/complete` 的 404 行為不變,只是補上明確
  的測試覆蓋。
