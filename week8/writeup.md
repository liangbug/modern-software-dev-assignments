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
Frameworks/Libraries Used: TODO
(Optional but recommended) Screenshots of core flows: TODO

REFLECTIONS:
===============
a. Issues encountered per stack and how you resolved them: TODO

b. Prompting (e.g. what required additional guidance; what worked poorly/wel): TODO

c. Approximate time-to-first-run and time-to-feature metrics: TODO
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
