# Week 6 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## Instructions

Fill out all of the `TODO`s in this file.

## Submission Details

Name: **TODO** \
SUNet ID: **TODO** \
Citations: **TODO**

This assignment took me about **TODO** hours to do.


## Brief findings overview

`semgrep-result.md` 掃出 3 大類問題，共 36 個 finding（0 個 blocking）：

1. **Supply Chain（依賴套件）**：`requirements.txt` 釘死一批舊版套件，帶出 1 個 Reachable
   （werkzeug CVE-2024-34069，CSRF，HIGH）、12 個 Undetermined（pydantic、requests、jinja2、
   werkzeug 的多個中等風險 CVE）、11 個 Unreachable（含 pyyaml 的 3 個 CRITICAL RCE，但目前
   程式沒有用到會觸發的 API，所以列為 unreachable）。
2. **Code Findings（12 個 non-blocking，但風險等級不低）**：`backend/app/main.py` 的 CORS
   wildcard、`backend/app/routers/notes.py` 與 `action_items.py` 的 `skip`/`limit` 分頁參數被
   taint 規則標記、`notes.py` 的 `unsafe_search` 是真的 SQL injection、`notes.py` 裡一批
   `/debug/*` 端點分別是任意程式碼執行（`eval`）、任意指令執行（`subprocess shell=True`）、
   SSRF（`urlopen`）、任意檔案讀取/路徑穿越（`open(path)`）。
3. 上述問題全部修掉，細節見下方 Fix #1～#5。

## Fix #1
a. File and line(s)
> `week6/requirements.txt`（全部 9 行；主要是第 4、5、6、7、8、9 行）

b. Rule/category Semgrep flagged
> Supply Chain：`werkzeug` CVE-2024-34069（HIGH，Reachable）、`pydantic` CVE-2024-3772 /
> CVE-2021-29510、`requests` CVE-2024-35195 / CVE-2023-32681 / CVE-2024-47081 /
> CVE-2026-25645、`jinja2` CVE-2024-34064 / CVE-2025-27516 / CVE-2024-22195 /
> CVE-2024-56326 / CVE-2020-28493、`werkzeug` CVE-2023-23934（LOW）等一系列 Undetermined
> finding，以及 pyyaml 的 3 個 CRITICAL RCE（Unreachable，但版本本身仍是漏洞版本）。

c. Brief risk description
> `requirements.txt` 鎖死的版本全部是多年前的舊版，橫跨 CSRF、XSS、ReDoS、無限迴圈、
> 憑證洩漏、不安全暫存檔等已知 CVE。即使部分目前 unreachable，只要程式碼未來多用到
> 一個 API（例如換成 `yaml.load` 而非 `safe_load`），就可能立刻變成可觸發的漏洞。

d. Your change (short code diff or explanation, AI coding tool usage)
> 把每個套件升到 semgrep 報告列出的「Fixed for X at version」對應版本：
> ```diff
> -pydantic==1.5.1
> -requests==2.19.1
> -PyYAML==5.1
> -Jinja2==2.10.1
> -MarkupSafe==1.1.0
> -Werkzeug==0.14.1
> +pydantic==2.4.0
> +requests==2.32.4
> +PyYAML==5.4
> +Jinja2==3.1.6
> +MarkupSafe==2.1.5
> +Werkzeug==3.0.6
> ```
> `fastapi`/`uvicorn`/`sqlalchemy` 沒被 semgrep 標出 CVE，維持原版本，避免不必要的相容性
> 風險。用 Claude Code 讀 semgrep 報告裡每一條 finding 的「Fixed for」欄位，逐一比對挑出
> 能同時修掉同套件全部已知 CVE 的最低版本號。

e. Why this mitigates the issue
> 升級到官方修補版本後，對應的 CVE 修補都已包含在該版本，掃描器對照的漏洞資料庫不會再
> 命中這些套件版本。

## Fix #2
a. File and line(s)
> `week6/backend/app/main.py:24`

b. Rule/category Semgrep flagged
> `python.fastapi.security.wildcard-cors.wildcard-cors`

c. Brief risk description
> `allow_origins=["*"]` 搭配 `allow_credentials=True`，等於任何網域都能帶著 cookie/認證
> 資訊呼叫這個 API，開發時方便，但上線後任何惡意網站都能跨網域打 API 並利用使用者已登入
> 的憑證。

d. Your change (short code diff or explanation, AI coding tool usage)
> ```diff
> -    allow_origins=["*"],
> +    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
> ```
> 改成明確列出本地開發前端會用到的來源清單。

e. Why this mitigates the issue
> CORS 改成白名單後，瀏覽器只會讓清單內的來源帶著憑證發起跨網域請求，其餘來源的請求會被
> 瀏覽器擋掉，消除任意網域濫用使用者 session 的風險。

## Fix #3
a. File and line(s)
> `week6/backend/app/routers/notes.py:18`、`week6/backend/app/routers/action_items.py:18`

b. Rule/category Semgrep flagged
> `python.fastapi.db.generic-sql-fastapi.generic-sql-fastapi`（taint 從 `skip: int = 0`
> 流到 `stmt.offset(skip).limit(limit)`）

c. Brief risk description
> Semgrep 的 taint 規則把「未加邊界限制的路徑參數流進資料庫查詢」一律視為潛在 SQL
> injection 來源。這裡 `skip` 雖然已經是 `int` 型別（FastAPI 會自動驗證型別），但沒有
> 下限限制，允許傳入負數，屬於缺乏輸入邊界驗證。

d. Your change (short code diff or explanation, AI coding tool usage)
> 兩個檔案都把 `skip: int = 0` 改成跟已有的 `limit: int = Query(50, le=200)` 一致的寫法：
> ```diff
> -    skip: int = 0,
> +    skip: int = Query(0, ge=0),
> ```

e. Why this mitigates the issue
> 明確加上 `ge=0` 讓 FastAPI/Pydantic 在進入函式前就擋掉非法輸入（例如負數分頁），同時
> 讓 semgrep 的 taint 規則能看到這個變數有經過驗證，不再視為未受控的輸入來源。SQL 本身
> 因為全程使用 SQLAlchemy Core 的 `.offset()/.limit()`（會綁定成參數化查詢，不是字串拼接）
> 而不構成真正的注入風險，這裡是把輸入驗證補齊，讓程式碼跟 semgrep 規則都更放心。

## Fix #4
a. File and line(s)
> `week6/backend/app/routers/notes.py:69-92`（原 `unsafe-search` 端點）

b. Rule/category Semgrep flagged
> `python.sqlalchemy.security.audit.avoid-sqlalchemy-text.avoid-sqlalchemy-text`、
> `python.fastapi.db.sqlalchemy-fastapi.sqlalchemy-fastapi`、
> `python.fastapi.db.generic-sql-fastapi.generic-sql-fastapi`

c. Brief risk description
> 原本的寫法直接把使用者輸入的 `q` 用 f-string 塞進 SQL 字串再交給 `text()` 執行：
> `WHERE title LIKE '%{q}%'`。這是教科書等級的 SQL injection——只要 `q` 帶入
> `' OR '1'='1` 之類字串，就能改變查詢邏輯甚至讀出所有資料。

d. Your change (short code diff or explanation, AI coding tool usage)
> 端點改名為 `search_notes`、路徑改成 `/notes/search`（拿掉 "unsafe" 字樣），SQL 改成用
> SQLAlchemy 的具名綁定參數，並把這個路由移到 `/{note_id}` 之前避免被該路由攔截：
> ```diff
> -    sql = text(
> -        f"""
> -        SELECT id, title, content, created_at, updated_at
> -        FROM notes
> -        WHERE title LIKE '%{q}%' OR content LIKE '%{q}%'
> -        ORDER BY created_at DESC
> -        LIMIT 50
> -        """
> -    )
> +    sql = text(
> +        """
> +        SELECT id, title, content, created_at, updated_at
> +        FROM notes
> +        WHERE title LIKE :pattern OR content LIKE :pattern
> +        ORDER BY created_at DESC
> +        LIMIT 50
> +        """
> +    ).bindparams(pattern=f"%{q}%")
>      rows = db.execute(sql).all()
> ```

e. Why this mitigates the issue
> `q` 不再被拼進 SQL 字串本身，而是透過 `:pattern` 綁定參數交給資料庫驅動，驅動會把它
> 當成單純的資料值處理，不會被解讀成 SQL 語法的一部分，因此任何 `q` 的內容都無法改變
> 查詢邏輯，SQL injection 的攻擊面被消除。

## Fix #5
a. File and line(s)
> `week6/backend/app/routers/notes.py:95-131`（原 `/debug/eval`、`/debug/run`、
> `/debug/fetch`、`/debug/read`、`/debug/hash-md5` 五個端點，已整批刪除）

b. Rule/category Semgrep flagged
> `python.fastapi.code.tainted-code-stdlib-fastapi.tainted-code-stdlib-fastapi` +
> `python.lang.security.audit.eval-detected.eval-detected`（`eval(expr)`）、
> `python.fastapi.os.tainted-os-command-stdlib-fastapi-secure-default...` +
> `python.lang.security.audit.subprocess-shell-true.subprocess-shell-true`
> （`subprocess.run(cmd, shell=True)`）、
> `python.lang.security.audit.dynamic-urllib-use-detected.dynamic-urllib-use-detected`
> （`urlopen(url)`）、
> `python.fastapi.file.tainted-path-traversal-stdlib-fastapi.tainted-path-traversal-stdlib-fastapi`
> （`open(path)`）

c. Brief risk description
> 這批端點把使用者傳入的字串直接丟進 `eval()`（任意程式碼執行）、
> `subprocess.run(cmd, shell=True)`（任意系統指令執行）、`urlopen(url)`（SSRF，可打內部
> 服務或讀 `file://` 本機檔案）、`open(path)`（任意檔案讀取/路徑穿越）。任何一個都能讓
> 攻擊者完全控制伺服器，是這次掃描裡風險最高的一組問題。

d. Your change (short code diff or explanation, AI coding tool usage)
> 直接刪除這五個 `/debug/*` 端點（含沒被標記出風險但同樣沒有正當用途的
> `debug_hash_md5`）。確認前先用 Grep 搜過 `backend/tests/`、`frontend/`，這些路徑沒有被
> 任何測試或前端程式呼叫，刪除不影響既有功能。

e. Why this mitigates the issue
> 這些端點對外開放且完全沒有輸入驗證，本質上就是留在生產路徑上的後門，任何「加驗證」的
> 修法都還是保留了攻擊面（例如白名單 `eval` 表達式仍有繞過風險）。既然沒有測試或功能依賴
> 它們，直接移除是最徹底也最符合最小攻擊面原則的作法——不存在的端點沒有漏洞可打。
