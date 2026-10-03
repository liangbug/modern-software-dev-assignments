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
Frameworks/Libraries Used: TODO
(Optional but recommended) Screenshots of core flows: TODO

REFLECTIONS:
===============
a. Issues encountered per stack and how you resolved them: TODO

b. Prompting (e.g. what required additional guidance; what worked poorly/wel): TODO

c. Approximate time-to-first-run and time-to-feature metrics: TODO
```
