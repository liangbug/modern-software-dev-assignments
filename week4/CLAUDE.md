# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 範圍

這是多週作業 repo 底下的 `week4/` 目錄（repo 根目錄的 `CLAUDE.md` 有跨週共通慣例）。Week 4 本身的任務目標，
依 `assignment.md`：在下方 starter app 之上,打造至少 2 個 Claude Code 自動化(`.claude/commands/*.md` slash
command、CLAUDE.md guidance、SubAgent 任選組合),再用這些自動化去擴充 starter app,並把設計與使用情形寫進
`writeup.md`。

目前狀態：
- `.claude/skills/refactor-module/SKILL.md`、`.claude/skills/run-test/SKILL.md` 已建立，是這份作業自己的
  交付物；`.claude/skills/sync-docs/` 目錄已建但尚未放 `SKILL.md`。
- `.claude/agents/{code-agent,db-agent,doc-agent,refactor-agent,test-agent}/` 五個資料夾已建立但都是空的
  —— SubAgent 設定還沒寫。
- 尚無 `.claude/commands/`（slash command 這條路還沒動工）。
- `writeup.md` 目前整份都是 TODO,尚未填寫。

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
  routers/notes.py       # /notes CRUD（目前只有 list/create/get）+ GET /notes/search/?q=
  routers/action_items.py
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

## 交付物同步檢查

- 自動化放在 `.claude/commands/*.md`（slash command）、`.claude/skills/*/SKILL.md`、`.claude/agents/*/`
  （SubAgent 設定）——判斷 Part I 是否完成前，先確認這些檔案真的存在且有記錄在 `writeup.md`。
- `writeup.md` 每個自動化固定要填：Design inspiration / Design / How to run / Before vs. after / How it
  enhanced the app 五段，隨自動化完成隨填，別留到最後一次補。
