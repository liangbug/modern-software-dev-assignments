# Week 8 Write-up
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


## App Concept
```
一個簡單的 Todo List app，讓使用者新增、刪除待辦事項，並可切換完成/未完成狀態。資料持久化於 SQLite，重新整理頁面後待辦清單仍會保留。
```


## Version #1 Description
```
APP DETAILS:
===============
Folder name: project1
AI app generation platform: bolt.diy
Tech Stack: TypeScript, Next.js (backend API routes) + React/Vite (frontend), Prisma ORM
Persistence: sqlite
Frameworks/Libraries Used: Next.js 14, Prisma Client 5, React 18, Vite 5, Tailwind CSS
(Optional but recommended) Screenshots of core flows: TODO

REFLECTIONS:
===============
a. Issues encountered per stack and how you resolved them: 前後端分離成兩個獨立 package（backend 用 Next.js API routes、frontend 用 Vite），一開始 bolt.diy 生成的 frontend API client 路徑與 backend 實際 route 對不上，手動調整 `frontend/src/api` 內的 base URL 後解決；Prisma schema 初次 `prisma db push` 時因 dev.db 檔案未建立而失敗，補跑一次即可。

b. Prompting (e.g. what required additional guidance; what worked poorly/wel): 單純描述「做一個 todo list app」效果普通，生成的 UI 很陽春；加上明確指定「用 Next.js + Prisma + SQLite 當後端、React + Vite + Tailwind 當前端」後，產出架構才符合預期。要求新增 completed 狀態切換功能時一次就生成正確。

c. Approximate time-to-first-run and time-to-feature metrics: 第一次用 bolt.diy，花不少時間熟悉介面與操作流程（約 60 分鐘），大半時間花在摸索環境設定與 prompt 寫法；熟悉後跑出第一版可用畫面約 15 分鐘，加上 CRUD 完整功能（新增/刪除/切換完成狀態）再花 20 分鐘。
```

## Version #2 Description
```
APP DETAILS:
===============
Folder name: project2
AI app generation platform: None
Tech Stack: Flask
Persistence: sqlite
Frameworks/Libraries Used: Flask 3.0.3, Python 標準庫 sqlite3（無額外 ORM）, pytest 8.3.3（測試用）, vanilla JS + Jinja2 template（前端）
(Optional but recommended) Screenshots of core flows: TODO

REFLECTIONS:
===============
a. Issues encountered per stack and how you resolved them: Flask app 用 `Flask(__name__)` 建立時，因為 `app/__init__.py` 屬於套件結構，預設的 template/static 資料夾會被解析成相對於 `app/` 目錄（即 `app/templates`），而不是專案根目錄的 `templates/`，導致首頁回傳 500（`TemplateNotFound`）。解法是在 `create_app()` 明確傳入絕對路徑的 `template_folder`、`static_folder`，指向專案根目錄下的 `templates/`、`static/`。另外測試中 `from app import create_app` 需要專案根目錄在 `sys.path` 上，透過新增 `pytest.ini` 設定 `pythonpath = .` 解決，避免測試執行位置依賴。

b. Prompting (e.g. what required additional guidance; what worked poorly/wel): 本版無使用 AI 生成平台，純手刻（符合 Flask 選擇輕量、無額外框架 overhead 的考量），因此無 prompting 紀錄；開發流程是直接依照 project1 的資料模型（id/title/completed/created_at/updated_at）與 REST 慣例（GET/POST /api/todos、PUT/DELETE /api/todos/:id）實作，保持 3 個版本的 API 語意一致，方便比較。

c. Approximate time-to-first-run and time-to-feature metrics: 搭建 Flask app 骨架（blueprint + sqlite3 helper）約 20 分鐘可跑起第一版空畫面；加上完整 CRUD API 與前端 vanilla JS 串接約再 25 分鐘；補 7 條 pytest 測試並排除上述 TemplateNotFound 問題約 15 分鐘。整體約 1 小時完成含測試的完整版本。
```

## Version #3 Description
```
APP DETAILS:
===============
Folder name: project3
AI app generation platform: None
Tech Stack: Vue.js + python FastAPI
Persistence: sqlite
Frameworks/Libraries Used: FastAPI 0.115.0, SQLAlchemy 2.0.35, Pydantic 2.9.2, uvicorn 0.30.6, pytest 8.3.3 + httpx（測試用）, Vue 3.4（`<script setup>`）, Vite 5

(Optional but recommended) Screenshots of core flows: TODO

REFLECTIONS:
===============
a. Issues encountered per stack and how you resolved them: Backend/frontend 是兩個獨立 process（FastAPI :8000、Vite dev server :5173），預設會觸發瀏覽器 CORS 限制，因此在 `app/main.py` 加上 `CORSMiddleware` 明確允許 `http://localhost:5173`。SQLAlchemy 2.0 的 `datetime.utcnow()` 預設值寫法會跳出棄用警告（`DeprecationWarning: datetime.datetime.utcnow() is deprecated`），改用 `datetime.now(UTC)` 包一層 helper function 解決。測試部分沿用 week2/4-7 starter app 的 `conftest.py` dependency override 慣例：用 `StaticPool` + in-memory sqlite 建立獨立 `TestingSessionLocal`，覆寫 `get_db` dependency，確保測試不會動到 `backend/data/todos.db`。

b. Prompting (e.g. what required additional guidance; what worked poorly/wel): 本版無使用 AI 生成平台，純手刻；為了跟 project1、project2 的資料模型與 API 路徑（/api/todos CRUD）保持一致，直接沿用相同欄位（id/title/completed/created_at/updated_at）與 REST 慣例，方便三個版本橫向比較同一組前端操作流程的實作差異。

c. Approximate time-to-first-run and time-to-feature metrics: Backend（FastAPI + SQLAlchemy model/schema/router）骨架約 25 分鐘可跑起 CRUD API；Frontend（Vue 3 + Vite，App/TodoList/TodoItem 三層元件拆分）串接 API 約再 20 分鐘；補 7 條 pytest 測試（含 in-memory DB fixture）約 15 分鐘，另花約 10 分鐘排除 CORS 與 datetime 棄用警告。整體約 1.5 小時完成含測試的完整版本（比 Flask 版久，主要是前後端分離多了一層 CORS 設定與元件拆分的時間）。
```
