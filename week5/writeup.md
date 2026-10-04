# Week 5 Write-up
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
### Automation A: Warp Drive saved prompts, rules, MCP servers

a. Design of each automation, including goals, inputs/outputs, steps
> 建了4個Warp Drive saved prompt + 1個repo rule：
> - **week5-test-runner**：跑`pytest -q {{target}} --cov=backend/app --cov-report=term-missing`，失敗的測試先重跑一次判定flaky（第二次過算flaky不算真失敗），對真失敗的讀錯誤訊息修到過。輸入：`target`（可選，指定單一測試路徑）。輸出：coverage%、flaky清單、改動檔案清單。連結：https://app.warp.dev/drive/prompt/week5-test-runner-AjDg4PQVM1VuOTKO7rRKJ1
> - **week5-docs-sync**：啟動`make run`背景執行，抓`/openapi.json`重新生成`docs/API.md`（依router分組列method/path/參數/回應schema），若舊檔已存在會在檔案最上方加"## Route Deltas"列出這次新增/移除/變更的路由。輸入：無。輸出：更新後的`docs/API.md`。連結：https://app.warp.dev/drive/prompt/week5-docs-sync-8yRvRLbutMBpj2LOzhT3za
> - **week5-refactor-harness**：`git mv old_path new_path`後全repo搜尋並更新所有import/reference，跑`make format && make lint && make test`確認沒壞。輸入：`old_path`、`new_path`（可選`old_symbol`/`new_symbol`）。輸出：改動檔案清單、rename前後對照。連結：https://app.warp.dev/drive/prompt/week5-refactor-harness-65D3V0B5AAvyRANVv6kc9s
> - **week5-release-helper**：跑完整檢查（format/lint/test），依`task_labels`生成changelog片段附加到`CHANGELOG.md`最上方，回報是否可安全push。輸入：`task_labels`（本次完成任務清單）。輸出：`CHANGELOG.md`新增段落、push可行性判定。連結：https://app.warp.dev/drive/prompt/week5-release-helper-6V00TsThfFeHd76htkY554
> - **week5-repo-rules**（`week5/AGENTS.md`）：只要工作目錄cd進`week5/`就自動套用，內容包含tech stack（FastAPI+SQLAlchemy+SQLite）、code architecture（routers/schemas/models路徑）、何時該用哪個saved prompt、Always/Never Do規則（例如「改完程式碼必須跑week5-test-runner，不可憑肉眼判斷」「重新命名檔案禁止手動改，必須用week5-refactor-harness」），還補了一條「一律用`uv run`」的Python環境規範，因為repo的venv只在最外層根目錄。

b. Before vs. after (i.e. manual workflow vs. automated workflow)
> 之前：每次改完程式碼要自己打`pytest`指令、肉眼判斷測試是不是flaky、手動去對openapi.json跟舊的`docs/API.md`比對差異、rename檔案要自己grep所有reference一個個改。
> 之後：agent對話框打`/`叫出Slash Commands選單、選saved prompt名字執行，flaky判定、文件同步、rename後的import修正都自動跑完並回報結果，不用自己再跑一輪指令核對。

c. Autonomy levels used for each completed task (what code permissions, why, and how you supervised)
> 給agent讀寫`week5/backend`、`week5/frontend`、`week5/backend/tests`的權限，可執行`make`系列指令（format/lint/test/run）。之所以放到這個範圍而不給更高權限，是因為每個任務的prompt都已經把涉及檔案範圍講清楚，agent不需要動到repo外的東西。監督方式：每個任務改完後人工看一次`git diff`，再跑一次`make test`確認全過才進commit。

d. (if applicable) Multi‑agent notes: roles, coordination strategy, and concurrency wins/risks/failures
> 見下方Automation B。

e. How you used the automation (what pain point it resolves or accelerates)
> 省掉「改完程式碼->手動跑測試->肉眼看是不是flaky->手動更新文件」這一整輪重複動作，尤其docs sync這件事人工做很容易忘記更新或漏列route deltas，交給saved prompt後每次任務結尾都會自動同步。



### Automation B: Multi‑agent workflows in Warp

a. Design of each automation, including goals, inputs/outputs, steps
> 用`git worktree`把「任務2：筆記搜尋分頁與排序」和「任務4：action items篩選+批量完成」拆成兩個獨立worktree/branch，各開一個Warp tab同時跑：
> ```
> git worktree add ../week5-task2 -b task2-search-pagination
> git worktree add ../week5-task4 -b task4-bulk-complete
> ```
> Tab A在`../week5-task2/week5`跑任務2的prompt，Tab B同時（不等A做完）在`../week5-task4/week5`跑任務4的prompt。兩邊各自跑`make test && make lint`過了才commit、push，回到主目錄`dev-light`分支各自merge回來，再跑一次整體`make test`確認合併後沒有互相踩到。

b. Before vs. after (i.e. manual workflow vs. automated workflow)
> 之前：一個任務做完、驗證過、commit完才能開始下一個任務，完全序列化。
> 之後：兩個檔案不重疊的任務（`routers/notes.py` vs `routers/action_items.py`）同時在兩個tab跑，時間上是並行而不是排隊，merge回主分支時因為改的檔案本來就沒重疊，沒有衝突。

c. Autonomy levels used for each completed task (what code permissions, why, and how you supervised)
> 兩個worktree各自獨立git狀態，agent只能動到自己worktree裡的檔案，天然隔離、不會互相干擾對方進度。監督方式：兩個tab各自跑完後才回主目錄做merge，merge前人工確認兩邊`git log`各自只有預期的commit。

d. (if applicable) Multi‑agent notes: roles, coordination strategy, and concurrency wins/risks/failures
> - 角色分工：Tab A（`task2-search-pagination`分支）負責筆記搜尋分頁排序，Tab B（`task4-bulk-complete`分支）負責action items篩選與批量完成。
> - 協調策略：靠git worktree物理隔離工作目錄，不共用檔案系統狀態，兩邊prompt事前就講清楚各自只碰哪個router檔案，避免同時改同一份檔案。
> - 並行結果：兩個branch各自的commit（`04db633`筆記搜尋分頁排序、`c5c4c35`行動項目篩選與批次完成）分別在`dae0bf0`、`fd2589e`merge回`dev-light`，merge過程沒有衝突，因為`notes.py`與`action_items.py`是不同檔案。沒有截圖存證這次的並行過程，用git branch/commit記錄佐證兩邊是各自獨立分支開發後才合併，而不是同一分支序列完成。

e. How you used the automation (what pain point it resolves or accelerates)
> 解決「多個獨立任務只能排隊做」的痛點，檔案不重疊時可以真正同時進行，縮短總體完成時間；worktree的隔離也讓两邊互不干擾，降低平行開發時互踩的風險。


### (Optional) Automation C: Any Additional Automations
a. Design of each automation, including goals, inputs/outputs, steps
> 除了SOP列的task2/task4以外，這次額外用同一套saved prompt+AGENTS.md規則陸續完成了任務3（Notes CRUD補完+前端optimistic update）、任務5（Tags多對多關聯）、任務6（擴充抽取邏輯，依賴任務5）、任務7（統一錯誤處理與回應包裝）、任務8（列表端點加分頁）、任務9（查詢索引與效能測試`backend/tests/test_performance.py`）、任務11（部署到Vercel，`api/index.py`+`vercel.json`）。每個任務都遵照AGENTS.md的Always Do規則：改完先跑`week5-test-runner`，API行為變動後跑`week5-docs-sync`同步`docs/API.md`。

b. Before vs. after (i.e. manual workflow vs. automated workflow)
> 之前：每個任務要自己記著先跑測試再跑文件同步這兩步，容易漏做，尤其像任務7（改全部既有測試斷言格式）這種影響面廣的任務。
> 之後：AGENTS.md的規則讓每個worktree/tab裡的agent都自動照做，不用每次任務都重新交代一次流程。

c. Autonomy levels used for each completed task (what code permissions, why, and how you supervised)
> 同Automation A，讀寫`backend/`、`frontend/`、`docs/`並可跑`make`指令；任務7因為會改動全部既有測試斷言，SOP明確標註不跟其他任務同時開兩個agent，所以是單獨、序列完成後才合併，避免跟其他任務互踩測試檔。

d. (if applicable) Multi‑agent notes: roles, coordination strategy, and concurrency wins/risks/failures
> 任務5→任務6有明確依賴（6要用5新增的Tag model），照SOP先後序列完成，不平行跑。

e. How you used the automation (what pain point it resolves or accelerates)
> AGENTS.md的Never Do規則（rename必須用week5-refactor-harness，不可手動改）在任務5新增Tag model、任務6接續擴充時避免了手動改檔案路徑漏改import的風險。
