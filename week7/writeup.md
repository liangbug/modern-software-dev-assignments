# Week 7 Write-up
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


## Task 1: Add more endpoints and validations
a. Links to relevant commits/issues
https://app.graphite.com/github/pr/liangbug/modern-software-dev-assignments/2

b. PR Description
- notes/action-items 新增 DELETE 與 /count 端點
- NoteCreate/NotePatch/ActionItemCreate/ActionItemPatch 加入
  非空白字串驗證，避免建立空白標題/內容/描述
- sort 參數改用欄位白名單取代 hasattr 判斷，避免排序到非預期屬性
- 補上對應測試（驗證失敗、404、count、delete）

c. Graphite Diamond generated code review
> Graphite Agent review 綠燈，未產生 actionable comment。

## Task 2: Extend extraction logic
a. Links to relevant commits/issues
https://app.graphite.com/github/pr/liangbug/modern-software-dev-assignments/3

b. PR Description
- 支援 checkbox 語法（- [ ] / - [x]，已勾選項目會被忽略）
- 支援數字編號清單（1. / 2)）
- 支援 @mention 指派對象與常見祈使動詞開頭（review/schedule/fix...）
- 抽取結果依內容去重，避免同一行重複出現多次
- 補上對應測試涵蓋各種新模式

c. Graphite Diamond generated code review
> Graphite Agent review 綠燈，未產生 actionable comment。

## Task 3: Try adding a new model and relationships
a. Links to relevant commits/issues
https://app.graphite.com/github/pr/liangbug/modern-software-dev-assignments/4

b. PR Description
- 新增 Tag 模型與 note_tags 關聯表（多對多）
- NoteCreate 支援 tag_names 建立時掛標籤；NoteRead 回傳 tags
- 新增 /tags 路由（list/create，依名稱冪等）
- notes 新增 POST/DELETE /notes/{id}/tags/{name|id} 掛載與移除標籤
- main.py 掛載 tags router；補上對應測試

c. Graphite Diamond generated code review
> Graphite Agent 指出 `tag_names` 欄位無驗證：note 建立時若傳入空白/空字串
> tag name（例如 `["work", "", " "]`），會被傳入 `get_or_create_tag()` 並被
> strip 成空字串，可能建立出無效的 Tag 紀錄或違反資料庫約束。建議在
> `NoteCreate.tag_names` 加上 `@field_validator`，逐一 strip 並過濾空字串
> /超長字串。
>
> 已採納：在 `schemas.py` 加上驗證，過濾空白與長度 >50 的 tag name，並用
> Graphite 的「Commit suggestion」直接套用。套用後另有一次在 `notes.py`
> 的 AI 建議被誤套成壞掉的重複程式碼（縮排錯亂、孤立的 `raise` 語句），
> 手動 review 發現後用 force-push 移除該 commit，只保留正確的
> `add_tag_to_note` 參數驗證版本。

## Task 4: Improve tests for pagination and sorting
a. Links to relevant commits/issues
https://app.graphite.com/github/pr/liangbug/modern-software-dev-assignments/5

b. PR Description
- 新增 test_pagination.py，涵蓋 notes 與 action-items 的
  skip/limit 分頁邊界、asc/desc 排序、未知 sort 欄位的
  fallback 行為、limit 上限驗證，以及 completed 篩選搭配分頁

c. Graphite Diamond generated code review
> Graphite Agent review 綠燈，未產生 actionable comment。

## Brief Reflection
a. The types of comments you typically made in your manual reviews (e.g., correctness, performance, security, naming, test gaps, API shape, UX, docs).
> 主要集中在 correctness（sort 白名單、驗證邊界）、test gaps（有沒有補到
> 404/空白輸入/邊界值的測試）、以及 API shape（新端點的 route 命名與
> response model 是否跟現有風格一致）。跨週共用的 starter app 架構讓我
> 比較容易發現「這個改動有沒有照現有 pattern 走」這類一致性問題。

b. A comparison of **your** comments vs. **Graphite’s** AI-generated comments for each PR.
> Task1、Task2、Task4 manual review 沒抓到額外問題，Graphite Agent 也判定綠燈，兩邊結論一致。
> Task3 上，Graphite Agent 抓到我 manual review 沒
> 注意到的 edge case：`tag_names` 傳入空白字串會被 strip 後仍嘗試建立
> Tag。我原本 review 只確認了「一般情況下 tag 建立正常」，沒特別測空白輸入這種邊界。

c. When the AI reviews were better/worse than yours (cite specific examples)
> 更好的例子：Task3 的 `tag_names` 空白驗證，AI 比我更早注意到這個邊界
> case，而且直接給出可套用的 validator code。
> 更差的例子：同一個 PR 裡，另一則 AI comment 的「Commit suggestion」
> 套用後在 `notes.py` 產生了縮排錯亂、含孤立 `raise` 語句的壞程式碼
> （commit `f678b6f`），本質上是 AI 生成的修正本身有 bug，一次性 apply
> 沒有先看過 diff 就會把壞 code 混進 PR。手動 line-by-line review 後才
> 發現並用 force-push 移除。

d. Your comfort level trusting AI reviews going forward and any heuristics for when to rely on them.
> 抓「有沒有考慮到某個 edge case」這類問題上 AI 很有用，值得信任、且比
> 我自己想得更全面。但 AI 給的「建議修正 code」不能無腦一鍵套用，尤其是
> 涉及多處縮排/多個 return 路徑的修改，套用後一定要重新看一次 diff、
> 跑一次測試再 commit，不能只看 comment 文字說得有道理就直接按
> Commit suggestion。heuristic：AI 找出的問題本身可信度高，AI 給的
> fix code 只能當草稿，要人工過一遍再套用。
