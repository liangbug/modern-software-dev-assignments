# SOP — Week 5 作業執行流程（任務1~8）

對應 `week5/assignment.md` 要求，本SOP保證兩個REQUIRED項目都做到：
- **(A) Warp Drive**：至少一個 saved prompt / rule / MCP server
- **(B) 多 agent 並行**：至少一次在不同 Warp tab（配 git worktree）同時跑獨立任務

實際只需挑2個以上任務完成即可交作業，但下面把 `docs/TASKS.md` 任務1~8 每一個都準備好對應SOP，你可以照自己時間挑要做哪些。

---

## Step 0 — 前置準備

```bash
cd week5
make run     # 確認目前app跑得起來
make test    # 確認目前測試全過，作為基準線
```

---

## Step 1 — 建立 Warp Drive 素材（滿足要求 A，一次做好，全部任務共用）

assignment.md列了5個範例（test runner、docs sync、refactor harness、release helper、Git MCP），只要求at least one，但5個都做，一次建齊，之後不用再補。每個Saved Prompt建立時Warp Drive表單都有 **Title / Description / Argument(s) / Prompt content** 四欄，缺一不可，下面逐一列出。

### 1a. Saved Prompt — `week5-test-runner`（對應「Test runner with coverage and flaky-test re-run」）

Warp裡 `Cmd/Ctrl+P` 開Command Palette搜尋 `New Prompt`，建：
```
Title: week5-test-runner
Description: 跑pytest+coverage，測試失敗的先重跑一次判定是否flaky，真失敗的自動修到過，回報coverage%與改動檔案。
Argument: target（可選，預設空字串。範例：backend/tests/test_notes.py::test_create_note，指定只跑單一測試）

Prompt content:
pytest -q {{target}} --cov=backend/app --cov-report=term-missing
若有測試失敗：
1. 記錄失敗清單
2. 每個失敗的測試單獨重跑一次（rerun once），若第二次通過則標記為 flaky 並列在報告最上面，
   不視為真正失敗
3. 對第二次仍失敗的測試，讀錯誤訊息去修 backend/app 或 backend/tests 對應程式碼，
   修完重跑該測試直到過
最後輸出：
- coverage總覆蓋率%
- flaky測試清單（若有）
- 這次改了哪些檔案
此流程不改變已通過的測試，重複執行結果應一致（idempotent）。
```
存檔後點 **Share**，複製連結。

### 1b. Saved Prompt — `week5-docs-sync`（對應「Docs sync: generate/update docs/API.md from /openapi.json」）

```
Title: week5-docs-sync
Description: 從執行中app的 /openapi.json 重新生成 docs/API.md，並在檔案最上方列出這次新增/移除/變更的路由（route deltas）。
Argument: 無

Prompt content:
先啟動 make run（背景執行，非互動），等 http://127.0.0.1:8000/openapi.json 有回應，
抓這個openapi spec，生成/更新 week5/docs/API.md：
- 依router分組（notes、action-items等）列出每個端點的 method、path、參數、回應schema範例
- 若 docs/API.md 已存在，比對新舊差異，在檔案最上方加一段 "## Route Deltas"
  列出這次新增/移除/變更的路由
完成後關閉背景的make run process。
這個流程每次執行只覆寫 docs/API.md，不動其他檔案，可重複執行（idempotent）。
```
存檔後點 **Share**，複製連結。

### 1c. Saved Prompt — `week5-refactor-harness`（對應「Refactor harness: rename a module, update imports, run lint/tests」）

```
Title: week5-refactor-harness
Description: 重新命名一個module/檔案（含對應import路徑），跑lint/test確認沒壞掉。用於任務間需要調整檔案結構或函式命名時，取代手動一個個找replace。
Argument: old_path, new_path, old_symbol（可選）, new_symbol（可選）
          範例：old_path=backend/app/services/extract.py
                new_path=backend/app/services/extraction.py

Prompt content:
1. 用 git mv {{old_path}} {{new_path}}（若old_path是資料夾內單一檔案，保留其他檔案不動）
2. 全repo搜尋所有 import/reference {{old_path}}（或 {{old_symbol}}）的地方，
   改成 {{new_path}}（或 {{new_symbol}}），包含 backend/app 與 backend/tests
3. 確認沒有殘留舊路徑/舊名字的reference（grep一次驗證）
4. 跑 make format && make lint && make test，全過為止
5. 回報：改了哪些檔案、rename前後對照
此流程對同一組old/new參數重複執行應該是no-op（idempotent，第二次跑找不到old_path會直接跳過）。
```
存檔後點 **Share**，複製連結。

### 1d. Saved Prompt — `week5-release-helper`（對應「Release helper: bump versions, run checks, prepare a changelog snippet」）

```
Title: week5-release-helper
Description: 幫week5這個作業階段性交付準備一份changelog片段，跑過所有檢查（format/lint/test），
             確認可以push的狀態，不動版本號（此repo無版本號機制，改成記錄"完成任務清單"的release note）。
Argument: task_labels（本次完成的任務清單，例如"任務2,任務4"）

Prompt content:
1. 跑 make format && make lint && make test，全過為止，沒過就先修
2. 用 git log 看這個branch這次做了哪些commit
3. 依 {{task_labels}} 生成一段changelog片段，格式：
   ## Week5 - {{task_labels}}
   - 變更摘要（列每個commit在做什麼）
   - 影響的API端點
   - 已知限制/待辦
4. 把這段changelog片段附加到 week5/CHANGELOG.md 最上方（若不存在就建立）
5. 回報目前是否可以安全push（測試/lint都過）
此流程每次執行只在CHANGELOG.md最上方新增一段，不覆寫既有內容，可重複執行。
```
存檔後點 **Share**，複製連結。

### 1e. Rule — 用 `week5/AGENTS.md`

Warp的Rule scope是靠檔案位置決定的：在 `week5/` 資料夾放一個 `AGENTS.md`（或`WARP.md`，兩者
Warp都認）檔案，Warp偵測到工作目錄cd進 `week5/` 就會自動套用這份rule，不需要另外在UI裡設定
「套用範圍」。這個repo已經有 `week5/AGENTS.md`（見下方），內容涵蓋tech stack、code architecture、
何時該用哪個saved prompt、Always/Never Do規則，不用再重建：

```markdown
# week5-repo-rules

## Tech Stack
- Backend: FastAPI
- ORM: SQLAlchemy
- Database: SQLite

## Code Architecture
- Routers (路由): backend/app/routers/
- Schemas (結構): backend/app/schemas.py
- Models (模型): backend/app/models.py

## Commands
- Test runner (測試): week5-test-runner
- Docs sync (文檔同步): week5-docs-sync
- Refactor tool (重構工具): week5-refactor-harness

## Rules & Boundaries

### Always Do
- 改完程式碼後，必須執行 week5-test-runner 進行自動測試確認，不可僅憑肉眼判斷。
- 新增或修改 API 行為時，必須同步更新 backend/tests/ 中對應的測試，並在完成後執行
  week5-docs-sync 以保持 docs/API.md 的即時同步。
- 保持現有的 response_model 風格，並與既有的程式碼命名慣例完全一致。

### Never Do
- 調整檔案結構或重新命名時，禁止手動修改，必須改用 week5-refactor-harness 來進行。
```
這份檔案本身就是可分享的素材（連同其他saved prompt定義一起放進 `week5/writeup.md`），
不需要另外去Warp Drive UI建立rule物件。若之後新增 `week5-release-helper` 的使用規則，
直接編輯這份 `AGENTS.md` 補上即可。

### 1f.（可選加分）Git MCP Server（對應「Integrate the Git MCP server」）
`Settings → AI → MCP Servers` 加Git MCP（依該MCP repo的command/args設定），讓agent能自主：
```
{
  "git": {
    "args": [
      "mcp-server-git"
    ],
    "command": "uvx"
  }
}
```
- 依任務名稱開branch（如 `git checkout -b task4-bulk-complete`）
- commit（訊息用 conventional commits格式）
- 產出PR note草稿（列出這次變更摘要）
設定完成後截圖存進writeup，並在一次任務中實際請agent透過MCP開branch+commit驗證有效。

> `week5/AGENTS.md`只要工作目錄cd進`week5/`就自動生效，不用手動套用。要跑某個saved prompt時，在agent對話框打 `/` 叫出Slash Commands選單，輸入prompt名字（如`week5-test-runner`）篩選後選取執行，不是打字當一般文字送出。這4個saved prompt（`week5-test-runner`、`week5-docs-sync`、`week5-refactor-harness`、`week5-release-helper`）＋`week5/AGENTS.md`＋（可選）Git MCP，share link/exported定義全部貼進 `week5/writeup.md`。

---

## Step 2 — 每個任務各自的 SOP（涉及檔案 + Warp prompt + 檢查重點）

固定收尾套路（每個任務做完都跑一次）：
```bash
make format && make lint && make test
git add -A && git commit -m "feat(week5): <任務名稱>"
```

### 任務1 — 前端遷移到 Vite + React（complex）
**涉及檔案**：`frontend/`（整個重建）、`Makefile`、`backend/app/main.py`（static mount）

**Prompt**：
```
在 week5/frontend/ 下用 Vite + React 建新前端，取代現有純HTML/CSS/JS。
- build產出到 week5/frontend/dist/
- 串接現有API: GET/POST /notes、GET /notes/{id}、GET /notes/search/、
  GET/POST /action-items（列出、建立、完成）
- 功能：筆記列表/新增/刪除/編輯；action item列表/新增/標記完成
- 更新 backend/app/main.py 的 StaticFiles mount，serve frontend/dist，
  根路徑"/"回傳 dist/index.html
- 更新 Makefile 加 web-install、web-dev、web-build target，
  make run 先跑 web-build 再啟動uvicorn
- 用React Testing Library幫至少2個元件寫測試
- 在 backend/tests 加API相容性測試
完成後執行 week5-test-runner，再跑 week5-docs-sync。
```
**檢查重點**：原有功能是否等價；`make run`是否還能一鍵啟動。

### 任務2 — 筆記搜尋分頁與排序（medium）
**涉及檔案**：`backend/app/routers/notes.py`、`backend/tests/test_notes.py`、前端搜尋UI

**Prompt**：
```
在 backend/app/routers/notes.py 實作 GET /notes/search，支援：
- q: 關鍵字（title/content不分大小寫比對）
- page、page_size（預設page=1, page_size=10）
- sort: created_desc 或 title_asc
回傳 { items: [...], total, page, page_size }，用SQLAlchemy組合
filter/order_by/limit/offset。
更新前端加搜尋框、結果筆數、上一頁/下一頁按鈕。
補測試：無結果、跨頁、排序正確性、q為空。
完成後執行 week5-test-runner，再跑 week5-docs-sync。
```
**檢查重點**：回應格式從list變成物件，前端呼叫端要一起改；既有測試斷言要跟著改。

### 任務3 — Notes完整CRUD + 前端optimistic update（medium）
**涉及檔案**：`backend/app/routers/notes.py`、`backend/app/schemas.py`、前端筆記編輯邏輯

**Prompt**：
```
在 backend/app/routers/notes.py 加：
- PUT /notes/{id}：更新title/content
- DELETE /notes/{id}：刪除，找不到回404
在 backend/app/schemas.py 的NoteCreate加驗證（title/content最小長度1，
最大長度合理值如title<=200, content<=5000）。
前端：編輯/刪除時先樂觀更新畫面，失敗時rollback並顯示錯誤。
補測試：更新成功、刪除成功、刪除不存在（404）、驗證失敗（422）。
完成後執行 week5-test-runner，再跑 week5-docs-sync。
```
**檢查重點**：加長度限制後，既有seed資料或測試字串是否超長。

### 任務4 — Action items篩選 + 批量完成（medium）
**涉及檔案**：`backend/app/routers/action_items.py`、`backend/app/schemas.py`、前端action item UI

**Prompt**：
```
在 backend/app/routers/action_items.py：
- GET /action-items 加 completed: bool | None 篩選參數
- 新增 POST /action-items/bulk-complete，body { ids: [int,...] }，
  同一transaction內標記完成，任一id不存在則整批rollback並回錯誤
前端加篩選toggle（全部/已完成/未完成）與批量勾選+完成按鈕。
補測試：篩選正確性、批量成功、批量部分失敗時整批rollback。
完成後執行 week5-test-runner，再跑 week5-docs-sync。
```
**檢查重點**：rollback是否真的生效（故意塞不存在的id，確認其他id沒被標記）。

### 任務5 — Tags多對多（complex）
**涉及檔案**：`backend/app/models.py`（新增Tag、note_tags關聯表）、新router`backend/app/routers/tags.py`、`backend/app/main.py`（掛router）、`services/extract.py`、前端tag UI

**Prompt**：
```
在 backend/app/models.py 加Tag model和note_tags多對多關聯表（Note<->Tag）。
新增 backend/app/routers/tags.py：
- GET /tags、POST /tags、DELETE /tags/{id}
- POST /notes/{id}/tags 附加tag、DELETE /notes/{id}/tags/{tag_id}移除
記得在 backend/app/main.py include這個新router。
更新 backend/app/services/extract.py：解析筆記文字中的#hashtag，
自動建立/附加對應tag。
前端：筆記顯示tag為chip，可依tag篩選筆記列表。
補測試：關聯建立/刪除、重複tag不重複建立、依tag篩選。
完成後執行 week5-test-runner，再跑 week5-docs-sync。
```
**檢查重點**：新model需要`data/app.db`重建或改`DATABASE_PATH`避免污染舊資料。

### 任務6 — 擴充抽取邏輯（medium，依賴任務5）
**涉及檔案**：`backend/app/services/extract.py`、`backend/app/routers/notes.py`（新增`/notes/{id}/extract`）

**Prompt**：
```
擴充 backend/app/services/extract.py 的 extract_action_items：
- 解析文字中的#hashtags -> 回傳tag清單
- 解析"- [ ] task text"格式的行 -> 回傳action item清單
在 backend/app/routers/notes.py 新增 POST /notes/{id}/extract：
- 回傳結構化抽取結果 { tags: [...], action_items: [...] }
- 若query帶apply=true，實際寫入DB（依任務5的tag model；若任務5沒做，
  先只處理action item部分）
補測試：純解析（不落庫）、apply=true落庫、混合文字。
完成後執行 week5-test-runner，再跑 week5-docs-sync。
```
**檢查重點**：跟任務5有依賴，先做任務5再做這個。

### 任務7 — 統一錯誤處理與回應包裝（easy-medium）
**涉及檔案**：`backend/app/main.py`（exception handler）、`backend/app/schemas.py`、`backend/tests/*`

**Prompt**：
```
在 backend/app/main.py 加全域exception handler：
- HTTPException -> { "ok": false, "error": { "code": "...", "message": "..." } }
- RequestValidationError（422） -> { "ok": false, "error": { "code": "VALIDATION_ERROR", "message": "..." } }
成功回應統一包成 { "ok": true, "data": <原回傳值> }。
在 backend/app/schemas.py 幫NoteCreate、ActionItemCreate加基本驗證（非空、最小長度1）。
更新既有測試，斷言改成 response.json()["data"] 或 ["error"]。
完成後執行 week5-test-runner，全部通過，再跑 week5-docs-sync。
```
**檢查重點**：影響面最廣，**不要**跟其他任務同時開兩個agent做（會互踩測試檔），單獨做完先合併。

### 任務8 — 所有列表端點加分頁（easy）
**涉及檔案**：`backend/app/routers/notes.py`、`backend/app/routers/action_items.py`、`backend/tests/*`、前端列表UI

**Prompt**：
```
在 backend/app/routers/notes.py 的 GET /notes 和
backend/app/routers/action_items.py 的 GET /action-items 加
page（預設1）、page_size（預設10）query參數。
回傳格式改為 { items: [...], total }。
用SQLAlchemy limit/offset實作。
前端列表加分頁控制（上一頁/下一頁、顯示第幾頁/共幾筆）。
補測試：0筆資料、最後一頁筆數不足、page_size超過總筆數、page超出範圍回空items。
完成後執行 week5-test-runner，再跑 week5-docs-sync。
```
**檢查重點**：回傳格式從list變成`{items, total}`，若任務7也做了要再包一層`data`；建議先做任務7再做任務8。

### 任務9 — 查詢效能與索引（easy-medium）
**涉及檔案**：`backend/app/models.py`、`backend/tests/test_performance.py`（新檔案）

**Prompt**：
```
在 backend/app/models.py 加SQLite索引：
- Note.title 加 index=True（/notes/search 的 title_asc 排序、比對用得到）
- note_tags 關聯表對 tag_id 額外加 Index（複合PK只覆蓋note_id方向，
  依tag篩筆記的反向查詢需要單獨索引）
新增 backend/tests/test_performance.py：
- seed較大資料集（如300筆notes），驗證分頁/排序/依tag篩選結果仍正確
- 用 EXPLAIN QUERY PLAN 驗證上述索引真的被用到（SQL文字含索引名）
完成後執行 week5-test-runner，再跑 week5-docs-sync。
```
**檢查重點**：`data/app.db`是舊schema建的，加索引不會自動套用到既有DB檔（`create_all`不會改已存在的table），本地驗證前先刪掉`data/app.db`讓它重建。

### 任務10 — 測試覆蓋率補強（easy）
**涉及檔案**：`backend/tests/test_notes.py`、`test_action_items.py`、`test_tags.py`

**Prompt**：
```
盤點現有測試，補齊每個端點缺的情境：
- GET /notes/{id} 找不到（404）
- POST /action-items 空description（422）
- PUT /action-items/{id}/complete 找不到（404）
- POST /tags 空name（422）
- POST /notes/{id}/tags 對不存在的note（404）
- 批量操作的並行/交易行為：用ThreadPoolExecutor同時送兩批不重疊id的
  bulk-complete請求，驗證兩批都正確完成、互不干擾
完成後執行 week5-test-runner，全部通過。
```
**檢查重點**：前端search/pagination/optimistic update整合測試在任務1、3、8時已經補齊（`NotesSection.test.jsx`），這裡只需補後端端點測試缺口。

### 任務11 — 部署到 Vercel（medium-complex）
**涉及檔案**：新增`week5/api/index.py`、`week5/vercel.json`、`week5/requirements.txt`；修改`backend/app/main.py`、`frontend/src/api.js`、`README.md`

**Prompt**：
```
讓week5可以部署到Vercel：
- 新增 week5/api/index.py，import backend/app/main.py 的 app，
  給 @vercel/python serverless function用
- 新增 week5/requirements.txt（fastapi、sqlalchemy、pydantic、
  python-dotenv），function的依賴用這份
- 新增 week5/vercel.json：buildCommand跑frontend的npm build，
  outputDirectory指到frontend/dist，rewrite /api/* 到api/index.py，
  其他路徑serve前端build
- frontend/src/api.js 所有fetch呼叫的路徑前綴改讀
  import.meta.env.VITE_API_BASE_URL（沒設就維持原本relative path，
  同源部署不受影響）
- backend/app/main.py 加CORSMiddleware，但只在環境變數ALLOWED_ORIGIN
  有設定時才加（同源部署時完全不啟用，前後端分開部署時才需要）
- README.md補一段部署guide：Vercel專案設定、環境變數、
  Option A（前後端都在Vercel，api/走serverless function）、
  Option B（後端另外部署到Fly.io/Render，前端在Vercel透過
  VITE_API_BASE_URL連外部API）、rollback方式
完成後執行 week5-test-runner（確認api.js改動沒讓現有前端測試斷言的
fetch URL斷掉），再跑 week5-docs-sync。
```
**檢查重點**：`api.js`的fetch URL加了base prefix後，前端測試mock裡斷言的URL字串（如`"/notes/search/?..."`）在測試環境`VITE_API_BASE_URL`未設時要維持原樣，跑一次`npm run test`確認沒斷。

---

## Step 3 — 用 git worktree + 多tab 平行跑（滿足要求 B）

**可平行組合**（檔案不重疊，風險最低）：
- 任務2（notes搜尋）＋ 任務4（action items篩選/批量）
- 任務8（分頁）＋ 任務4（篩選/批量）— 若都碰 `action_items.py` 建議先講清楚各自只動哪個函式

**不建議平行**：任務7單獨做，不跟其他任務同時開，因為它會改動全部既有測試斷言。

**有依賴、不能真平行**：任務5 → 任務6（6依賴5的model），要先後做。

實際操作（以任務2＋任務4為例）：

```bash
git worktree add ../week5-task2 -b task2-search-pagination
git worktree add ../week5-task4 -b task4-bulk-complete
```

**Tab A：**
```bash
cd ../week5-task2/week5
```
貼任務2的prompt。

**Tab B（跟Tab A同時進行，不要等A做完才開）：**
```bash
cd ../week5-task4/week5
```
貼任務4的prompt。

兩個tab同時在跑時，截圖存證（兩個Agent視窗都在working中的畫面），存進 `week5/screenshots/`。

---

## Step 4 — 各自驗證與合併

```bash
# Tab A
cd ../week5-task2/week5
make test && make lint
git add -A && git commit -m "feat(week5): 任務2 筆記搜尋分頁排序"
git push -u origin task2-search-pagination

# Tab B
cd ../week5-task4/week5
make test && make lint
git add -A && git commit -m "feat(week5): 任務4 action items篩選與批量完成"
git push -u origin task4-bulk-complete
```

回主目錄合併：
```bash
cd week5
git merge task2-search-pagination
git merge task4-bulk-complete
make test
git worktree remove ../week5-task2
git worktree remove ../week5-task4
```

---

## Step 5 — 寫 `week5/writeup.md`

```markdown
# Writeup

## 自動化1：week5-test-runner（Warp Drive saved prompt）
- 目標：跑pytest+coverage，flaky測試自動重跑一次判定，失敗的自動修到過
- 輸入：{{target}}（可選，指定單一測試路徑）　輸出：coverage%、flaky清單、改動檔案
- 分享連結：<貼Warp Drive share link>

## 自動化2：week5-docs-sync（Warp Drive saved prompt）
- 目標：從 /openapi.json 生成/更新 docs/API.md，並列出route deltas
- 輸入：無　輸出：docs/API.md（含變更摘要）
- 分享連結：<貼Warp Drive share link>

## 自動化3：week5-refactor-harness（Warp Drive saved prompt）
- 目標：重新命名module/檔案並同步更新import，跑lint/test確認沒壞
- 輸入：old_path, new_path（可選old_symbol, new_symbol）　輸出：rename前後對照、lint/test結果
- 分享連結：<貼Warp Drive share link>

## 自動化4：week5-release-helper（Warp Drive saved prompt）
- 目標：跑完整檢查（format/lint/test）並生成本次完成任務的changelog片段
- 輸入：task_labels（本次完成的任務清單）　輸出：CHANGELOG.md新增段落、是否可push的判定
- 分享連結：<貼Warp Drive share link>

## 自動化5：week5-repo-rules（Warp Drive rule）
- 目標：讓每個agent tab都遵守專案結構慣例，並自動呼叫上面幾個saved prompt
- 內容：<貼rule全文>

## （若做了）自動化6：Git MCP整合
- 目標：讓agent自主開branch/commit/寫PR note
- 設定：<貼MCP設定截圖或config>
- 驗證：<實際跑一次自動開branch+commit的過程與結果>

## 完成任務與難度
- 任務X（難度）：...
- 任務Y（難度）：...

## Before vs After
- 之前：逐一手動做、來回跑指令
- 之後：多任務同時在不同tab進行，saved prompt統一驗證

## 自主程度
- 給agent權限：讀寫week5/backend、frontend、tests，可跑make指令
- 監督方式：每個worktree改完人工看diff、跑一次make test再push

## 多agent筆記
- 角色分工：Tab A做任務X，Tab B做任務Y
- 協調策略：git worktree各自獨立分支
- 並行結果：<實際同時跑幾個agent、有無衝突、花多久>

## 使用心得（解決什麼痛點）
- <實際感受>
```

---

## 收尾檢查表

- [ ] 至少完成2個 `docs/TASKS.md` 任務，各自標註難度
- [ ] Warp Drive 至少1個 saved prompt/rule/MCP，share link寫進writeup
- [ ] 至少一次真正同時在不同tab跑agent，有截圖佐證
- [ ] `week5/writeup.md` 五個小節都填
- [ ] `make test`、`make lint` 全過
