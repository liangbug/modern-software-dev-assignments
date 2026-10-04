# Week 2 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## INSTRUCTIONS

Fill out all of the `TODO`s in this file.

## SUBMISSION DETAILS

Name: **TODO** \
SUNet ID: **TODO** \
Citations: **TODO**

This assignment took me about **TODO** hours to do. 


## YOUR RESPONSES
For each exercise, please include what prompts you used to generate the answer, in addition to the location of the generated response. Make sure to clearly add comments in your code documenting which parts are generated.

### Exercise 1: Scaffold a New Feature
Prompt: 
```
分析 week2/app/services/extract.py extract_action_items() 啟發式函式。
實作新函式 extract_action_items_llm(text: str) -> List[str]，
透過 gemini_client.chat() 呼叫 Gemini API；
從 .env 讀GEMINI_API_KEY、GEMINI_MODEL 環境變數；
System prompt 要有角色、任務，語言繁體中文，markdown format；
設定options參數，使模型輸出結構化 JSON 陣列，回傳乾淨待辦事項字串列表。
``` 

Generated Code Snippets:
```
extract.py:68-107
```

### Exercise 2: Add Unit Tests
Prompt: 
```
在 week2/tests/test_extract.py 為 extract_action_items_llm() 寫測試:
- 單元測試 (mock chat()，涵蓋情境: 條列清單、關鍵字開頭行 todo:/action:/next:、空輸入、LLM 回傳非 JSON 時 fallback 空列表)
- 整合測試 (不 mock chat()，直接打真實 Gemini API，驗證回傳為非空字串列表；GEMINI_API_KEY 或 GEMINI_MODEL 未設定時自動 skip)
``` 

Generated Code Snippets:
```
teste_extract.py:26-106
```

### Exercise 3: Refactor Existing Code for Clarity
Prompt: 
```
重構 week2 的 FastAPI 後端以提升可讀性：
把 app/routers/notes.py 與 app/routers/action_items.py 裡原始 Dict[str, Any] 請求/回應資料，換成正式 Pydantic schema。
整理 app/db.py 資料庫存取層。
init_db() 從模組匯入時執行，改成放進 app/main.py FastAPI lifespan/startup 事件。
各 router 加一致錯誤處理（正確用 HTTPException 與輸入驗證）。
``` 

Generated/Modified Code Snippets:
```
schemas.py (new file — Pydantic models for notes and action items)
app/db.py:78-87 (new get_action_item())
app/main.py:1-24 (lifespan-based init_db(), imports cleanup)
app/routers/notes.py:1-28 (Pydantic request/response models, error handling)
app/routers/action_items.py:1-56 (Pydantic request/response models, 404 handling via db.get_action_item/db.get_note)
```


### Exercise 4: Use Agentic Mode to Automate a Small Task
Prompt: 
```
(1) app/routers/action_items.py 新增端點，對外提供 LLM 抽取功能（extract_action_items_llm）。frontend/index.html 加「Extract LLM」按鈕，點擊呼叫該端點，顯示結果。
(2) app/routers/notes.py 新增 GET 端點回傳所有筆記。frontend/index.html 加「List Notes」按鈕，點擊抓取顯示所有筆記。
兩按鈕對應 JS fetch 呼叫與畫面渲染都要串接好。
``` 

Generated Code Snippets:
```
app/routers/action_items.py:36-47 (new /action-items/extract-llm endpoint)
app/routers/notes.py:21-24 (new GET /notes endpoint)
frontend/index.html:27-28, 39-40, 62-84 (Extract LLM / List Notes buttons + fetch handlers)
```


### Exercise 5: Generate a README from the Codebase
Prompt: 
```
分析 week2 的程式碼庫（FastAPI 應用、SQLite 儲存、Gemini 驅動的抽取功能、前端頁面），
在 week2/ 底下生成一份 README.md，內容至少包含：
專案簡介、環境設定與啟動方式（uv/poetry + uvicorn）、API 端點與其功能說明、以及如何用 pytest 執行測試套件。
``` 

Generated Code Snippets:
```
README.md
```


## SUBMISSION INSTRUCTIONS
1. Hit a `Command (⌘) + F` (or `Ctrl + F`) to find any remaining `TODO`s in this file. If no results are found, congratulations – you've completed all required fields. 
2. Make sure you have all changes pushed to your remote repository for grading.
3. Submit via Gradescope. 