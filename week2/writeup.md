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
TODO
``` 

Generated/Modified Code Snippets:
```
TODO: List all modified code files with the relevant line numbers. (We anticipate there may be multiple scattered changes here – just produce as comprehensive of a list as you can.)
```


### Exercise 4: Use Agentic Mode to Automate a Small Task
Prompt: 
```
TODO
``` 

Generated Code Snippets:
```
TODO: List all modified code files with the relevant line numbers.
```


### Exercise 5: Generate a README from the Codebase
Prompt: 
```
TODO
``` 

Generated Code Snippets:
```
TODO: List all modified code files with the relevant line numbers.
```


## SUBMISSION INSTRUCTIONS
1. Hit a `Command (⌘) + F` (or `Ctrl + F`) to find any remaining `TODO`s in this file. If no results are found, congratulations – you've completed all required fields. 
2. Make sure you have all changes pushed to your remote repository for grading.
3. Submit via Gradescope. 