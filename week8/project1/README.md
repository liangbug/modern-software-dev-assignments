# Todo List — Next.js + Prisma + Vite (Version #1)

簡單 Todo List app：新增、刪除待辦事項，切換完成/未完成狀態，資料持久化於 SQLite。前後端分離成兩個獨立專案（由 bolt.diy 生成）。

## Tech Stack
- Backend: Next.js 14 (App Router API routes) + Prisma ORM 5
- Frontend: React 18 + Vite 5 + Tailwind CSS
- Persistence: SQLite (`backend/prisma/dev.db`)

## Prerequisites
- Node.js 18+
- pnpm

## Install

```bash
cd week8/project1/backend
pnpm install
pnpm prisma:generate
pnpm prisma:push   # 建立 dev.db，首次執行需要

cd ../frontend
pnpm install
```

## Run

需要開兩個 terminal，分別啟動 backend、frontend：

```bash
# terminal 1
cd week8/project1/backend
pnpm dev        # http://localhost:3000

# terminal 2
cd week8/project1/frontend
pnpm dev        # http://localhost:5173
```

開啟 http://localhost:5173 使用前端畫面。

## Env Configuration

`backend/.env`：
```
DATABASE_URL="file:./dev.db"
```

`frontend/.env`：
```
VITE_API_BASE_URL=http://localhost:3000
```

## API
| Method | Path              | Body                                        |
|--------|-------------------|----------------------------------------------|
| GET    | /api/todos        | -                                            |
| POST   | /api/todos        | `{ "title": string }`                       |
| PUT    | /api/todos/:id    | `{ "title"?: string, "completed"?: bool }`  |
| DELETE | /api/todos/:id    | -                                            |

## Known Issues / Manual Notes
- Backend (Next.js, port 3000) 與 frontend (Vite, port 5173) 是兩個獨立 process，需各自啟動；API route 已加 CORS header 允許跨來源請求。
- 由 bolt.diy 生成，首次生成後手動調整過 `frontend/src/api` 內的 API base URL 才能對上 backend 實際路由；`prisma db push` 需手動補跑一次才會建立 `dev.db`。
- 未加入 CSRF/身份驗證保護；此為課堂練習用 app，非生產環境設計。
