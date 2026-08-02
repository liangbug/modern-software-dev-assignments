# Week 2 – Action Item Extractor

以 FastAPI + SQLite 打造小應用，把自由格式筆記（會議記錄、待辦清單）轉成結構化的 action item 清單。支援兩種抽取方式：規則式（正規表示式 heuristic）與 LLM 式（Gemini API）。

## 專案架構

```
week2/
├── app/
│   ├── main.py                # FastAPI app、lifespan、靜態檔案掛載
│   ├── db.py                  # SQLite 連線與 CRUD（notes / action_items 表）
│   ├── schemas.py              # Pydantic request/response models
│   ├── routers/
│   │   ├── notes.py            # /notes 端點
│   │   └── action_items.py     # /action-items 端點
│   └── services/
│       ├── extract.py          # 規則式 + LLM 式抽取邏輯
│       └── gemini_client.py    # Gemini API 包裝（仿 ollama.chat() 介面）
├── frontend/
│   └── index.html              # 純 HTML/JS 前端（無框架）
├── tests/
│   └── test_extract.py         # pytest 測試（含 mock 與可選的真實 API 整合測試）
└── data/
    └── app.db                  # SQLite 檔案（執行時自動建立）
```

資料庫：兩張表 `notes`（id, content, created_at）與 `action_items`（id, note_id, text, done, created_at），`init_db()` 於 app 啟動時（lifespan）自動建表。

## 環境設定與啟動

前置需求：Python >= 3.10，套件管理用專案根目錄的 `pyproject.toml`（uv）。

### 1. 安裝依賴

於根目錄執行：
```bash
uv sync
```

### 2. 設定環境變數

在專案根目錄建立 `.env`（`extract.py` 用 `python-dotenv` 載入），LLM 抽取功能需要：
```
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.0-flash-lite   # 或其他可用 Gemini 模型
```
沒設定時，`extract_action_items_llm()` 呼叫會因缺少 `GEMINI_API_KEY` 而丟例外；規則式端點 `/action-items/extract` 不受影響。

### 3. 啟動伺服器

```bash
uv run uvicorn week2.app.main:app --reload
```

啟動後開瀏覽器到 http://127.0.0.1:8000/ 即可看到前端頁面。

## API 端點

### Notes

| Method | Path | 說明 |
|---|---|---|
| POST | `/notes` | 建立一筆筆記。Body: `{"content": "..."}`，`content` 不可為空白。回傳 `NoteResponse`（id, content, created_at）。 |
| GET | `/notes` | 取得所有筆記，依 id 由新到舊排序。 |
| GET | `/notes/{note_id}` | 取得單一筆記，不存在回 404。 |

### Action Items

| Method | Path | 說明 |
|---|---|---|
| POST | `/action-items/extract` | 用規則式 heuristic（`extract_action_items`）從 `text` 抽取 action item。Body: `{"text": "...", "save_note": bool}`。若 `save_note=true` 會先把 `text` 存成一筆 note，抽出的項目連同 `note_id` 一起存入 `action_items`。回傳 `note_id` 與 `items`（每項含 id, text）。 |
| POST | `/action-items/extract-llm` | 同上，但改用 Gemini LLM（`extract_action_items_llm`）抽取，要求模型輸出 JSON 字串陣列（`response_mime_type: application/json`）。需要 `GEMINI_API_KEY`、`GEMINI_MODEL` 環境變數。 |
| GET | `/action-items?note_id=` | 列出 action items，可用 `note_id` 篩選；`note_id` 不存在時回 404。 |
| POST | `/action-items/{action_item_id}/done` | 標記/取消完成狀態。Body: `{"done": bool}`。項目不存在回 404。 |

### 規則式抽取邏輯（`extract_action_items`）

- 匹配項目符號（`-`、`*`、`•`、`1.`）、`todo:`/`action:`/`next:` 前綴、或 `[ ]`/`[todo]` checkbox 標記的行。
- 去除前綴/標記後輸出，並去重（忽略大小寫）。
- 若整篇文字都沒有匹配到，改用句子切分＋祈使句起始字（add/create/fix/...）當 fallback。

### LLM 式抽取邏輯（`extract_action_items_llm`）

- 用系統提示詞要求 Gemini 抽取待辦事項，並用 `response_schema` 強制輸出字串陣列的 JSON。
- 解析失敗（非 JSON、非陣列）時回傳空陣列，不丟例外。

## 前端

`frontend/index.html` 是無框架的原生 HTML/JS 頁面，由 `/` 端點直接回傳，靜態資源另外掛在 `/static`。功能：
- 貼上筆記文字，勾選是否存成 note。
- 「Extract」按鈕呼叫 `/action-items/extract`；「Extract LLM」按鈕呼叫 `/action-items/extract-llm`。
- 抽出的項目可勾選 checkbox 標記完成（呼叫 `/action-items/{id}/done`）。
- 「List Notes」按鈕呼叫 `/notes` 列出所有已存筆記。

## 執行測試

測試在 `week2/tests/test_extract.py`，涵蓋規則式抽取、LLM 抽取（用 `unittest.mock.patch` mock 掉 `gemini_client.chat`，覆蓋 bullet list、keyword 前綴、空輸入、非 JSON 回應等情境）。

於專案根目錄執行：
```bash
uv run pytest week2/tests/ -v
```

其中一項測試（`test_extract_action_items_llm_real_api`）會打真實 Gemini API，僅在同時設定 `GEMINI_API_KEY` 與 `GEMINI_MODEL` 環境變數時才會執行，否則自動 skip。
