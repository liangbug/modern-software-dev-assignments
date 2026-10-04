# Todo List — Vue.js + FastAPI (Version #3)

簡單 Todo List app：新增、刪除待辦事項，切換完成/未完成狀態，資料持久化於 SQLite。Backend 與 frontend 為獨立 process。

## Tech Stack
- Backend: FastAPI + SQLAlchemy 2.0 + Pydantic 2
- Frontend: Vue 3 (`<script setup>`) + Vite
- Persistence: SQLite (`backend/data/todos.db`，首次啟動自動建立)

## Prerequisites
- Python 3.10+
- Node.js 18+

## Backend — Install & Run

```bash
cd week8/project3/backend
python -m venv .venv
.venv\Scripts\activate       # Windows
# source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API 會在 http://localhost:8000，health check：`GET /health`。

### Backend Tests

```bash
python -m pytest tests -v
```

測試使用記憶體內 SQLite（透過 FastAPI dependency override），不會動到 `data/todos.db`。

## Frontend — Install & Run

```bash
cd week8/project3/frontend
npm install
npm run dev
```

開啟 http://localhost:5173

## Env Configuration
- Frontend: 複製 `.env.example` 為 `.env`，設定 `VITE_API_BASE_URL`（預設 `http://localhost:8000`）。
- Backend: 不需額外環境變數，SQLite 路徑固定為 `backend/data/todos.db`。

## API
| Method | Path              | Body                                        |
|--------|-------------------|-----------------------------------------------|
| GET    | /api/todos        | -                                               |
| POST   | /api/todos        | `{ "title": string }`                          |
| GET    | /api/todos/:id    | -                                               |
| PUT    | /api/todos/:id    | `{ "title"?: string, "completed"?: bool }`     |
| DELETE | /api/todos/:id    | -                                               |

## Known Issues / Manual Notes
- Backend 與 frontend 是跨 port 的兩個獨立 process，透過 FastAPI `CORSMiddleware` 允許 `http://localhost:5173`；部署時需依實際網域調整 `allow_origins`。
- 未加入身分驗證，此為課堂練習用 app，非生產環境設計。
