---
name: sync-docs
description: >
  檢查並修補 week4 這個 FastAPI 筆記 app 的文件落差(drift)——一是 backend 實際 API
  (routers/notes.py、routers/action_items.py、FastAPI 產生的 /openapi.json)跟文件描述的
  endpoint 是否一致;二是 CLAUDE.md、week4/CLAUDE.md、writeup.md 描述的檔案結構/交付物狀態
  (.claude/skills、.claude/agents、.claude/commands 底下實際有哪些檔案)是否跟目前 repo 狀態
  一致。當使用者講「sync docs」「文件同步」「檢查文件漂移」「docs 跟 code 對不對得上」「文件過期了
  嗎」時使用此 skill。找到落差後直接修文件文字並回報改了什麼,不需使用者一項項確認——只改文件,不
  碰程式邏輯。
---

# sync-docs

Week4 這個 repo 有兩層文件,容易跟 code 脫節:

1. **API 文件漂移**:`routers/notes.py`、`routers/action_items.py` 的實際路徑/方法,跟任何提
   到這些 endpoint 的文件(CLAUDE.md 架構段、docs/TASKS.md 若有列 endpoint 清單)不一致。
2. **交付物狀態漂移**:`week4/CLAUDE.md`「目前狀態」段落描述 `.claude/skills/`、
   `.claude/agents/`、`.claude/commands/`、`writeup.md` 的完成度,跟這些檔案實際內容不一致
   (例如某 skill 已經寫好 SKILL.md,但 CLAUDE.md 還寫「尚未放 SKILL.md」)。

這兩種漂移都是「文件說謊」——會誤導下一個讀 CLAUDE.md 的人(包含你自己)。抓到就直接修正文字,
不用每條都停下來問,因為這類修正是低風險、可逆的(純文字,git diff 一看就懂)。

## 步驟

### 1. 抓實際 API 現況

在 `week4/` 目錄下(需要 `PYTHONPATH=.`):

```bash
PYTHONPATH=. python -c "from backend.app.main import app; import json; print(json.dumps(app.openapi(), ensure_ascii=False, indent=2))"
```

PowerShell:
```powershell
$env:PYTHONPATH = "."; python -c "from backend.app.main import app; import json; print(json.dumps(app.openapi()))"
```

同時直接讀 `backend/app/routers/notes.py`、`backend/app/routers/action_items.py` 確認每個
`@router.get/post/put/delete(...)` 的路徑、參數、回傳型別(`schemas.py` 裡對應的 `*Read`)。

### 2. 抓文件現況

讀:
- 根目錄 `CLAUDE.md`(跨週共通慣例,通常不會描述 week4 具體 endpoint,但要看有沒有過期的架構描述)
- `week4/CLAUDE.md`「架構」與「目前狀態」段落
- `week4/writeup.md`
- `week4/docs/TASKS.md`(若列了 endpoint 或任務清單)

### 3. 比對「目前狀態」段落 vs 實際檔案

`week4/CLAUDE.md` 的「目前狀態」逐條對照實際檔案系統:

```bash
ls .claude/skills/*/SKILL.md
ls .claude/agents/*/
ls .claude/commands/ 2>/dev/null
```

- 某 skill 資料夾底下已經有 `SKILL.md` 但 CLAUDE.md 寫「尚未建立」→ 漂移
- 某 agent 資料夾已經有設定檔但 CLAUDE.md 寫「都是空的」→ 漂移
- `writeup.md` 的 Automation #1/#2 段落已經填了內容但 CLAUDE.md 寫「整份都是 TODO」→ 漂移

### 4. 比對 API 文件段落 vs 實際 routers

`week4/CLAUDE.md` 架構段目前這樣描述 notes router:

> `routers/notes.py # /notes CRUD(目前只有 list/create/get)+ GET /notes/search/?q=`

若之後有人加了 update/delete、改了 search 參數、或 action_items 加了完成流程的 endpoint,這行
會過期。逐一核對:
- 文件宣稱有的方法,程式碼真的有嗎?
- 程式碼有的方法,文件提到了嗎?
- query/path 參數名稱、預設值是否還對得上?

### 5. 動手修

發現落差後直接用 Edit 修正文字,原則:

- **只改文件敘述,絕不改程式邏輯**——這是 sync-docs 的職責邊界,行為變更留給
  refactor-module 或使用者自己處理。
- 修完保留段落原本的語氣跟繁體中文寫法,只更新跟事實不符的部分,不要整段重寫。
- 若某段落籠統到無法用一行更新(例如整段都過期),才整段改寫,並保留原有結構(標題層級、
  bullet 風格)。

### 6. 回報

修完列出:
- 改了哪個檔案、哪一段
- 改之前 vs 改之後(一兩行摘要即可,不用整段貼)
- 若有「疑似漂移但不確定」的項目(例如程式碼行為模糊、文件描述本來就是概略性的),列出來但不動
  手,交由使用者判斷

## 邊界

- 不確定某個 endpoint 是不是刻意設計成跟文件不同(例如 TASKS.md 列的是「待做」而非「現況」)時,
  不要硬改——只有「文件宣稱是現況但跟程式碼不符」才算漂移。
- 不修改 `docs/TASKS.md` 的任務清單本身(那是待辦事項,不是現況描述),除非任務已完成卻還列在
  清單上。
