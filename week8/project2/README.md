# Todo List — Flask (Version #2)

簡單 Todo List app：新增、刪除待辦事項，切換完成/未完成狀態，資料持久化於 SQLite。

## Tech Stack
- Backend: Flask 3 + 標準庫 `sqlite3`（無額外 ORM）
- Frontend: Jinja2 template + vanilla JS（同源，無需 CORS）
- Persistence: SQLite (`data/todos.db`，首次啟動自動建立)

## Prerequisites
- Python 3.10+

## Install

```bash
cd week8/project2
python -m venv .venv
.venv\Scripts\activate       # Windows
# source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

## Run

```bash
python run.py
```

開啟 http://localhost:5000

## Tests

```bash
python -m pytest tests -v
```

測試使用暫存資料庫，不會動到 `data/todos.db`。

## Env Configuration
不需額外環境變數。資料庫檔案路徑預設為 `data/todos.db`，相對於專案根目錄建立。

## API
| Method | Path              | Body                              |
|--------|-------------------|------------------------------------|
| GET    | /api/todos        | -                                   |
| POST   | /api/todos        | `{ "title": string }`              |
| PUT    | /api/todos/:id    | `{ "title"?: string, "completed"?: bool }` |
| DELETE | /api/todos/:id    | -                                   |

## Known Issues / Manual Notes
- 單一 Flask process 同時提供 API 與前端頁面，開發時僅需啟動一個 server。
- 未加入 CSRF 保護；此為課堂練習用 app，非生產環境設計。
