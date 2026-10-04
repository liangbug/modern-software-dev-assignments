# Week 4 Write-up
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
### Automation #1 — `refactor-module` + `run-test` 兩個Skill組合
a. 設計靈感(引用best-practices和/或sub-agents文件)
> 依best-practices文件中「每個自動化單位的職責要窄、要能獨立驗證」的原則,把「重構」跟「跑測試驗證」拆成
> 兩個各自獨立、單一職責的Skill,而不是寫成一個大而全的command。兩者刻意分工:`refactor-module`只負責
> 結構調整(不改行為),`run-test`只負責驗證行為(不做結構調整);使用時先跑前者、再跑後者,形成一個
> 「改結構→驗證行為沒變」的最小工作流。

b. 各自動化的設計,包含目標、輸入輸出、步驟
> 兩個Skill都放在`week4/.claude/skills/`底下(`refactor-module/SKILL.md`、`run-test/SKILL.md`)。
> - **refactor-module** — 輸入:一個既有程式檔或模組路徑。步驟:讀懂目標檔案與對應測試 → 找出重構動機
>   (函式過長、重複邏輯、命名模糊、職責混雜等壞味道,沒有壞味道就不動) → 規劃拆法 → 用`Edit`套用,
>   維持公開簽名/回傳值/路由行為不變 → 跑`make format && make lint` → 若有既有測試就跑對應測試核對行為
>   沒變,沒有測試覆蓋就明確告知使用者「這塊靠人工核對」。輸出:結構調整後的diff,以及一段可直接貼進
>   writeup.md「Before vs. after」的說明。
> - **run-test** — 輸入:剛完成的一次改動(或使用者指定的測試範圍)。步驟:先確認在`week4/`目錄下操作、
>   判斷這次要跑全套還是只跑相關測試 → 執行`make test`或指定的`pytest`指令 → 全過就回報通過數量;有失敗
>   就先完整讀懂traceback、判斷是測試預期錯還是實作真的有bug,只修造成失敗的那部分,改完重新跑一次確認
>   轉綠,再跑一次全套確認沒有連帶弄壞其他測試。輸出:一份「跑了什麼範圍、結果如何、若修了什麼原因」的
>   驗證結論。

c. 執行方式(確切指令)、預期輸出、rollback/safety notes
> 在互動式Claude Code session中(`.claude/skills/`底下的skill會被自動載入),對Claude說出符合skill
> `description`觸發語意的請求即可自動觸發,例如「幫我重構`services/extract.py`」會觸發`refactor-module`,
> 「這個改動有沒有破壞測試」會觸發`run-test`;也可以用`/refactor-module`、`/run-test`明確呼叫。底層實際
> 執行的指令是`make format && make lint`(refactor-module收尾)以及`make test`或
> `pytest -q backend/tests/test_xxx.py::test_yyy`(run-test)。
> Rollback/safety note:兩個Skill都只做「結構調整」或「驗證」,不改變API契約、不動`data/app.db`、不跳過
> pre-commit;若重構或修測試改到公開行為,兩個skill都會在交付前明確提醒使用者確認,而不是默默改掉。若
> 跑出來的結果不如預期,直接用`git diff`/`git checkout -- <file>`還原單一檔案即可,兩個skill都不涉及
> 資料庫或不可逆操作。

d. Before vs. after(即手動流程vs.自動化流程)
> Before:重構跟驗證常常混在同一輪修改裡做——邊重構邊順手改邏輯,或改完結構才想到要跑測試,導致行為
> 有沒有跑掉全靠事後回想,難以對照。而且每次都要自己想「這次該跑哪些測試」、失敗了要自己從頭讀
> traceback。
> After:兩個步驟拆開、各自有固定檢查清單。`refactor-module`保證每次重構都會自問「這一步只改了怎麼做,
> 沒有改做出什麼結果嗎」,並強制收尾跑`make format && make lint`；`run-test`保證每次驗證都會先完整讀懂
> 失敗原因才動手改,改完必定重跑確認轉綠,不會「改完就交差」。整套流程從「憑印象」變成「有固定步驟可
> 依循、有明確通過/失敗結論」。

e. 如何用這個自動化擴充starter application
> 實際用於`docs/TASKS.md`中「`extract.py`的tag解析」相關的前置整理:先用`refactor-module`把
> `backend/app/services/extract.py`裡原本混在一起的逐行解析邏輯拆成獨立的小函式(`_split_lines`、
> `_match_action_item`等),確認`make format && make lint`乾淨、且既有測試全數通過、行為未變;再用
> `run-test`針對這次重構跑`pytest -q backend/tests/test_extract.py`確認沒有連帶弄壞其他測試。這次重構
> 完成後,才交棒給Automation #2的六角色SubAgent pipeline去實際新增`tags`欄位這個功能——先把舊邏輯整理
> 乾淨,新功能才不會疊加在混亂的基礎上。


### Automation #2 — Six-role SubAgent pipeline (Plan → DB → Refactor → Test → Code → Docs)
a. 設計靈感(引用best-practices和/或sub-agents文件)
> 依SubAgents概覽文件(docs.anthropic.com/en/docs/claude-code/sub-agents)以及`assignment.md`section C
> 提供的三組範例流程(TestAgent+CodeAgent、DocsAgent+CodeAgent、DBAgent+RefactorAgent)為基礎。沒有做成
> 三組互不相關的demo pair,而是把三組合併成一條有順序的pipeline,並在最前面加第六個角色`plan-agent`,
> 產出一份共享的規劃文件供其餘五個角色讀取——這遵循best-practices文件「每個subagent的context跟職責要
> 窄」(role-specialized)的指引,以及「用checklist/scratchpad在角色之間交棒,而不是依賴隱含的共享狀態」
> 的建議。

b. 各自動化的設計,包含目標、輸入輸出、步驟
> 六個SubAgent定義檔放在`week4/.claude/agents/{plan-agent,db-agent,refactor-agent,test-agent,
> code-agent,doc-agent}.md`(扁平檔案,frontmatter為`name`/`description`/`tools`)。每個角色都有明確的
> 檔案範圍界線,職責不重疊:
> - **plan-agent** — 讀取`docs/TASKS.md`裡的一項任務,寫出`docs/plans/<task-slug>/{design.md,tasks.md,
>   testing.md}`(實作計畫、各角色任務checklist、given/when/then測試情境)。只碰`docs/plans/`。
> - **db-agent** — 讀`design.md`的schema段落,只編輯`backend/app/models.py`+`data/seed.sql`(若選擇
>   自動migration選項,也會動`backend/app/db.py`)。必須為既有`data/app.db`檔案記錄rollback/相容性
>   注意事項。
> - **refactor-agent** — 把新欄位套用到`backend/app/schemas.py`/router簽名上(僅結構層,不寫業務邏輯),
>   然後跑`make format && make lint`。
> - **test-agent** — 只寫/改`backend/tests/`,做法二選一:(a)依`testing.md`寫出會失敗的新測試,或
>   (b)跑`make test`驗證並回報通過/失敗與具體assertion diff。絕不碰`backend/app/`。
> - **code-agent** — 只在`backend/app/`裡實作,讓test-agent寫的失敗測試轉綠,完成後自行用`make test`+
>   `make format && make lint`自我檢查。
> - **doc-agent** — 在測試轉綠後,更新`docs/API.md`與`docs/TASKS_DONE.md`(`docs/TASKS.md`本身是唯讀,
>   絕不編輯或標註),並標出`writeup.md`裡需要填寫的段落——絕不碰程式碼。
> 順序由依賴關係決定,不是隨意排列:schema要先存在,模型才能被測試;結構要先套用,測試才能被收集
> (collect);測試要先寫(TDD),再寫實作;文件最後寫,因為文件描述的是最終、已底定的狀態。

c. 執行方式(確切指令)、預期輸出、rollback/safety notes
> 在互動式Claude Code session中(`.claude/agents/`底下的custom subagent會被即時載入),依序呼叫各角色,
> 例如`@plan-agent 規劃 docs/TASKS.md 第4項...`,接著`@db-agent ...`等,或讓Claude依各agent的
> `description`觸發語意自動委派。每一步完成後,在`week4/`目錄下跑`make test`/`make lint`,確認符合預期
> 的紅→綠轉換。
> Rollback/safety note(此次執行由db-agent撰寫):SQLite的`Base.metadata.create_all`不會對既有table做
> `ALTER TABLE`,所以在這次改動前就存在的本機`data/app.db`,之後任何碰到新欄位的查詢都會丟出
> `OperationalError: no such column: notes.tags`。此repo沒有migration工具、也沒有真實資料,因此
> 記錄的rollback做法是:刪除`data/app.db`,重新跑`make run`/`make seed`以新schema重建。測試不受影響——
> `backend/tests/conftest.py`的`client` fixture永遠使用全新的暫存DB。

d. Before vs. after(即手動流程vs.自動化流程)
> Before:一個橫跨schema+業務邏輯+測試+文件的改動,意味著要在`models.py`、`schemas.py`、`routers/`、
> `services/`、`backend/tests/`、`docs/`之間手動來回切換,全部塞在一段冗長、沒有結構的session裡——很容易
> 搞不清楚哪個檔案已經「定案」、哪個還在變動中,文件更新也常常被跳過,或是在API形狀還沒定案前就先寫
> (導致立刻產生drift)。
> After:同一個改動拆成六個有界限的步驟,角色之間有明確的交棒產物(`design.md`/`tasks.md`/`testing.md`,
> 之後每個角色的diff在git上可見)。每一步的範圍窄且可檢核(「db-agent是不是真的只碰了models.py跟
> seed.sql?」),而文件保證在測試轉綠之後才寫,所以`API.md`/`TASKS.md`描述的是實際交付的行為,而不是
> 進行中的猜測。

e. 如何用這個自動化擴充starter application
> 針對`docs/TASKS.md`第4項(「改善抽取邏輯」)實際跑過一次完整六步pipeline:為`Note`新增`tags`欄位
> (db-agent),把它串進`NoteRead`(refactor-agent),寫了8個新測試覆蓋`extract_tags`的解析規則以及
> `/notes/`建立+讀取的round-trip(test-agent),在`services/extract.py`裡實作`extract_tags()`並串進
> `POST /notes/`(code-agent),重新驗證全部11個測試轉綠、lint乾淨(test-agent),並在新建的
> `docs/API.md`裡記錄新的`tags`欄位,同時在`docs/TASKS_DONE.md`記錄完成狀態——`docs/TASKS.md`本身維持
> 未變動(doc-agent)。規劃文件留存在`docs/plans/note-tags/`,作為這次執行的證據。


### *(Optional) Automation #3*
*If you choose to build additional automations, feel free to detail them here!*

a. Design inspiration (e.g. cite the best-practices and/or sub-agents docs)
> TODO

b. Design of each automation, including goals, inputs/outputs, steps
> TODO

c. How to run it (exact commands), expected outputs, and rollback/safety notes
> TODO

d. Before vs. after (i.e. manual workflow vs. automated workflow)
> TODO

e. How you used the automation to enhance the starter application
> TODO
