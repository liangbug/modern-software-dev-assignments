# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 範圍

這是多週作業 repo 底下的 `week4/` 目錄（repo 根目錄的 `CLAUDE.md` 有跨週共通慣例）。Week 4 本身的任務目標，
依 `assignment.md`：在下方 starter app 之上,打造至少 2 個 Claude Code 自動化(`.claude/commands/*.md` slash
command、CLAUDE.md guidance、SubAgent 任選組合),再用這些自動化去擴充 starter app,並把設計與使用情形寫進
`writeup.md`。

目前狀態：
- `.claude/skills/refactor-module/SKILL.md`、`.claude/skills/run-test/SKILL.md`、
  `.claude/skills/sync-docs/SKILL.md` 三個 skill 都已建立，是這份作業自己的交付物。
- `.claude/agents/{plan-agent,db-agent,refactor-agent,test-agent,code-agent,doc-agent,
  orchestrator-agent}.md` 七個 SubAgent 定義檔已建立（扁平放在 `.claude/agents/` 下，不是子資料夾），
  並已實跑過一次完整流程：`plan-agent → db-agent → refactor-agent → test-agent → code-agent →
  test-agent → doc-agent`，練習任務是 `docs/TASKS.md` 第 4 項（Note 新增 `tags` 欄位、`extract.py`
  解析 `#tag`）。規劃文件留在 `docs/plans/note-tags/{design.md,tasks.md,testing.md}`。
  `orchestrator-agent` 負責依 `tasks.md` 分工依序呼叫其餘五個角色 agent。
- 尚無 `.claude/commands/`（slash command 這條路還沒動工）。
- `writeup.md` 的 Automation #2（六角色 SubAgent pipeline）已填寫完成；Automation #1 與
  Automation #3（optional）欄位仍是 TODO。

## 指令（在 `week4/` 目錄內執行）

```bash
make run     # uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
make test    # pytest -q backend/tests
make format  # black . && ruff check . --fix
make lint    # ruff check .
make seed    # python -c "from backend.app.db import apply_seed_if_needed; apply_seed_if_needed()"
```

單獨跑一個測試：`pytest -q backend/tests/test_notes.py::test_create_note`。Makefile 會 export
`PYTHONPATH := .`；若不透過 `make` 直接跑 pytest/uvicorn，記得自行設定 `PYTHONPATH=.`（PowerShell 用
`$env:PYTHONPATH = "."`）。

## 架構

```
backend/app/
  main.py               # FastAPI app：把 frontend/ mount 成 static，啟動時建表 + seed DB
  db.py                 # SQLAlchemy engine/session（SQLite 位於 data/app.db，可用 DATABASE_PATH 覆寫）；
                         # apply_seed_if_needed() 只在 data/app.db 第一次不存在時載入 data/seed.sql
  models.py             # Note、ActionItem 兩個 SQLAlchemy models
  schemas.py            # Pydantic *Create / *Read 成對出現
  routers/notes.py       # /notes CRUD（list/create/get/update/delete）+ GET /notes/search/?q=
  routers/action_items.py # /action-items（list/create + PUT /{id}/complete）
  services/extract.py    # extract_action_items(text) —— 逐行啟發式抽取
frontend/                # 純 HTML/CSS/JS，無 build step，由 FastAPI StaticFiles 提供
data/app.db, data/seed.sql
docs/TASKS.md            # 一批離散任務，設計上是拿來練習 agent 驅動工作流程的靶子
```

測試用 `backend/tests/conftest.py` 裡的 `client` fixture，把 `get_db` 換成暫存檔 SQLite DB，所以測試永遠不
會動到 `data/app.db`。

### `docs/TASKS.md` —— 拿來驅動自動化的候選任務

pre-commit 設置、`/notes/search` 擴充、action item 完成流程、`extract.py` 的 tag 解析、notes CRUD（編輯/
刪除）、request 驗證與錯誤處理、對 `/openapi.json` 的文件漂移檢查。建自動化時優先拿這些任務當練習對象，
別在示範自動化時另外發明不相關的功能。

## Code navigation / entry points

- 啟動 app：`make run`（`uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000`），進入點
  `backend/app/main.py`。
- Router 在 `backend/app/routers/`：`notes.py`（/notes CRUD + /notes/search/）、
  `action_items.py`（/action-items，含 PUT /action-items/{id}/complete）。新增 endpoint 從這裡下手。
- 測試在 `backend/tests/`，共用 fixture 在 `backend/tests/conftest.py`（`client` fixture 把 `get_db`
  換成暫存 SQLite，不會動到 `data/app.db`）。跑法：`make test` 或單獨
  `pytest -q backend/tests/test_notes.py::test_create_note`。
- DB seed：`backend/app/db.py` 的 `apply_seed_if_needed()`，只在 `data/app.db` 第一次不存在時套用
  `data/seed.sql`。手動重跑：`make seed`。

## Style / safety guardrails

- Formatter/linter：black（line-length 100）+ ruff（`select = ["E","F","I","UP","B"]`，
  `ignore = ["E501","B008"]`），設定在 repo 根目錄 `pyproject.toml`，適用整個 repo。改完程式一定跑
  `make format && make lint`。
- 安全可跑的指令：`make run`、`make test`、`make lint`、`make format`、`make seed`、單獨 `pytest`。
- 避免：改動 `data/app.db`（測試永遠用暫存 DB，不該手動去動這個檔案）、跳過 pre-commit
  （`--no-verify`）、直接改 `data/seed.sql` 卻不確認既有 `app.db` 不受影響、對外部服務發送請求。
- Gate：合併/交付前，`make lint` 跟 `make test` 都要過；新增/修改 endpoint 一定要有對應測試。

## Workflow snippets

- 新增 endpoint 時：先在 `backend/tests/` 寫一個會失敗的測試 → 在對應 router
  （`backend/app/routers/*.py`）實作 → 需要的話同步補 `schemas.py` 的 Pydantic 模型 → 跑
  `make test` 確認轉綠 → 跑 `make format && make lint` 後再交付。
- 修 bug 時：先重現（跑相關測試或手動呼叫 API）→ 定位到 `services/`、`routers/` 或 `models.py` →
  修正 → 跑 `make test` 全跑一次確認沒有連帶壞掉別的測試。
- 改完 API 形狀（新增/刪除欄位、endpoint）後，記得檢查 `/openapi.json` 跟文件（`writeup.md`、
  `docs/TASKS.md`）有沒有跟著漂移，需要時用 `sync-docs` skill 補上。

## 交付物同步檢查

- 自動化放在 `.claude/commands/*.md`（slash command）、`.claude/skills/*/SKILL.md`、`.claude/agents/*/`
  （SubAgent 設定）——判斷 Part I 是否完成前，先確認這些檔案真的存在且有記錄在 `writeup.md`。
- `writeup.md` 每個自動化固定要填：Design inspiration / Design / How to run / Before vs. after / How it
  enhanced the app 五段，隨自動化完成隨填，別留到最後一次補。
