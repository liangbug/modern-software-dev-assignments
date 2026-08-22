# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 專案性質

這是 CS146S（史丹佛大學「The Modern Software Developer」課程）的每週作業集合。每個 `weekN/` 目錄都是
**獨立、自成一體的作業** —— 除非某檔案明確跨目錄 import（實際上沒有；各週是重複複製 starter app，而非共用
程式碼），否則不要假設各週之間有共用程式碼或設定。處理任務時,將注意力限定在任務指定的那個 `weekN/` 目錄內。

## 環境與安裝

- Python 3.12，用 `uv` 管理（另外還有舊版 `pyproject-poetry.toml`/`poetry.lock` 供 Poetry 使用，但根目錄的
  `uv.lock` + `pyproject.toml` 才是主要管理方式）。
- 安裝依賴：`uv sync`（若用 Poetry 則 `poetry install --no-interaction`）。
- 機密資訊（Gemini API key 等）放在根目錄的 `.env`（`.gitignore` 已排除，勿提交）。
- 根目錄 `pyproject.toml` 統一設定 `black`（line-length 100）與 `ruff`（`select = ["E","F","I","UP","B"]`,
  `ignore = ["E501","B008"]`），適用整個 repo。`.pre-commit-config.yaml` 執行 black、ruff --fix、
  end-of-file-fixer、trailing-whitespace。

## 常用指令

Week 4–7 各自有自己的 `Makefile`（要在該 `weekN/` 目錄內執行），目標完全相同：

```bash
make run     # uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
make test    # pytest -q backend/tests
make format  # black . && ruff check . --fix
make lint    # ruff check .
make seed    # python -c "from backend.app.db import apply_seed_if_needed; apply_seed_if_needed()"
```

Makefile 會 export `PYTHONPATH := .`，讓 `backend.app.*` 的 import 能解析 —— 若不透過 `make`、直接手動跑指令，
記得先在該 `weekN/` 目錄下自行設定 `PYTHONPATH=.`。

單獨跑一個測試：`pytest -q backend/tests/test_notes.py::test_create_note`（在 `weekN/` 目錄內執行）。

Week 1 是獨立腳本（`python week1/k_shot_prompting.py` 等），沒有 server 或測試。
Week 2 是最初版的 FastAPI+SQLite app，早於 Makefile 慣例出現，要在 `week2/` 目錄內直接用
`uv run uvicorn week2.app.main:app --reload`（從 repo 根目錄）執行；測試用
`uv run pytest week2/tests/ -v`。
Week 3 是 MCP server：`uv run --group week3 python week3/server/main.py`（STDIO transport，直接執行會停在那邊
等 JSON-RPC client，這是預期行為，不是卡住）；測試用 `uv run --group week3 pytest week3/tests -q`。

## 重複出現的 starter app 架構（week 2、4–7）

這些週次都是重新實作同一個最小應用 —— 一個能把自由格式筆記抽取成「action item」清單的筆記 app —— 每週有
小幅變化（這正是作業重點：在同一個基礎上練習 agent 驅動的重構、安全修補、code review 等）。架構固定如下：

```
backend/app/
  main.py              # FastAPI app：把 frontend/ mount 成 static，啟動時建表 + seed DB，掛載 routers
  db.py                # SQLAlchemy engine/session（SQLite 位於 data/app.db，可用 DATABASE_PATH 覆寫路徑）；
                        # apply_seed_if_needed() 只在第一次執行時載入 data/seed.sql
  models.py            # SQLAlchemy declarative models：Note、ActionItem
  schemas.py           # Pydantic request/response models（*Create / *Read 成對出現）
  routers/
    notes.py           # /notes 端點（CRUD + /notes/search/）
    action_items.py    # /action-items 端點
  services/
    extract.py         # extract_action_items(text)：從筆記文字抽出 action item
                        # （多數週次是啟發式的逐行抽取；若要換成 LLM 抽取邏輯可參考 week1/ 的 prompting 技巧）
frontend/               # 純 HTML/CSS/JS，無 build step，由 FastAPI 的 StaticFiles 提供
data/
  app.db                # SQLite 檔案，第一次執行時自動建立
  seed.sql              # 僅在 app.db 不存在時套用的種子資料
```

測試（`backend/tests/`）用 `conftest.py` 裡的 `client` fixture，透過 FastAPI 的 dependency override 把
`get_db` 換成暫存檔 SQLite DB，所以測試永遠不會動到 `data/app.db`。

比較各週差異時，`diff -rq weekX/backend weekY/backend` 是最快的方式 —— 每週的差異通常集中在一兩個檔案
（例如 `services/extract.py`、`routers/notes.py`）。

### 各週差異重點

- **week2**：最初版，扁平結構是 `app/`（不是 `backend/app/`），沒有 Makefile，也沒有 `docs/TASKS.md`。
- **week4**：作業目標是打造至少 2 個 Claude Code 自動化（slash command、CLAUDE.md、SubAgent，任選組合），
  再用這些自動化去擴充下方 starter app（見 `week4/assignment.md`）。目前 `.claude/skills/` 下已有
  `refactor-module`（重構模組並自動跑 format/lint）與 `run-test`（依變更範圍挑測試、跑 pytest、修到過）兩個
  skill，是這份作業自己的交付物，不是既有基礎設施；`writeup.md` 要記錄每個自動化的設計與使用情形。
- **week5**：同一套 starter app，用來練習 Warp 的 agentic workflow，app 本身沒有特別的 repo 差異。
- **week6**：Semgrep 安全掃描/修補練習的目標，`backend/`、`frontend/` 內預期有刻意埋入的漏洞；另外多了一份
  `requirements.txt`（除了 `uv`/`pyproject` 之外），因為 Semgrep 會直接掃依賴清單檔。
- **week7**：有 `docs/TASKS.md` 列出一批離散的實作任務，設計上是一個任務對一個 branch、一次性 AI prompt完成，
  再各自 review、開成獨立 PR。
- **week8**：沒有起始程式碼 —— 是從零開始、自選技術棧的作業（見 `week8/assignment.md`），要求同一個 app 用
  三種不同技術棧各實作一次，其中至少一版要用 `bolt.new` 生成，至少一版前端或後端要用非 JavaScript 語言。

## 其他週次補充

- **week1**：prompting 技巧練習（k-shot、chain-of-thought、self-consistency、reflexion、RAG、tool calling），
  透過 `week1/gemini_client.py` 呼叫 Gemini（介面模仿舊版 `ollama.chat()`）。需要根目錄 `.env` 裡的
  `GEMINI_API_KEY`。
- **week3**：建立MCP server（`week3/server/arxiv_client.py`）。
