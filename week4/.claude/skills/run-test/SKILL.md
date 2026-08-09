---
name: run-test
description: 用於在week4這個FastAPI筆記應用中執行測試——依變更範圍挑出該跑的測試、執行`pytest`、解讀失敗訊息並修到通過。當使用者說「跑測試」「run test」「測試失不失敗」「幫我測一下」「這個改動有沒有破壞測試」時,主動使用此skill,即使沒有明確講出`pytest`或`make test`,只要意圖是驗證程式行為是否正確,也應觸發。修完bug後會自動重跑測試確認真的通過,不會只改完就交差。
---

# Run Test

在`week4/`底下執行、解讀、修復測試的skill。目標:每次改動後,拿到一個「測試真的通過」的結論,不是猜的。

## 核心原則

跑測試跟修測試是兩個階段,不要跳著做。先看清楚失敗原因,再動手改——不要看到紅字就亂猜著改,改完又不重跑確認。而且只修測試揭露出的問題,不要順手夾帶其他改動,不然對照不出這次改動到底解決了什麼。

## 執行步驟

### 1. 確認工作目錄與範圍

先確認在`week4/`目錄下操作(不是repo根目錄或其他week)。看使用者這次改了什麼:
- 若剛編輯過某個檔案(例如`backend/app/services/extract.py`),優先找對應的測試檔(`backend/tests/test_*.py`裡跟這個模組相關的)。
- 若不確定改動範圍或使用者要求「全部跑一遍」,直接跑整個測試套件。
- 若使用者指名了某個測試函式,精準只跑那一個,不要放大範圍浪費時間。

### 2. 執行測試

用`make test`跑整套(它會自動設好`PYTHONPATH=.`並跑`pytest -q backend/tests`)。若只需要跑單一測試檔或函式:

```bash
cd week4
PYTHONPATH=. pytest -q backend/tests/test_notes.py::test_create_note
```

Windows PowerShell下設環境變數語法不同,若在PowerShell執行,改用:

```powershell
$env:PYTHONPATH = "."
pytest -q backend/tests/test_notes.py::test_create_note
```

### 3. 全部通過的情況

直接跟使用者回報:跑了哪些測試、共幾個通過。不用多加解釋。若這次跑測試是某個功能改動的收尾(對應`docs/TASKS.md`裡的某項任務),提醒使用者可以把這個結果補進`writeup.md`的「Before vs. after」區塊。

### 4. 有失敗的情況

1. 完整讀懂失敗的traceback——是assertion不符、exception、還是fixture出錯。不要只看最後一行就下結論。
2. 回頭看被測的程式碼(`backend/app/`下對應的router/service/model),搞清楚是測試寫錯了預期,還是程式邏輯真的有bug。
3. 只改動造成失敗的那部分,不要連帶重構或加功能——這是`run-test`的邊界,結構性改動請改用`refactor-module`這個skill。
4. 改完後**重新跑一次**剛剛失敗的測試,確認真的轉綠。若還是失敗,回到步驟1重新分析,不要重複套用同一個猜測性修法。
5. 修完後,順手跑一次全套`make test`,確認沒有因為這次修改連帶弄壞其他原本通過的測試。

### 5. 找不到對應測試的情況

如果改動的程式碼在`backend/tests/`底下完全沒有對應測試覆蓋,明確跟使用者說「這塊目前沒有測試保護」,不要假裝有跑過驗證。可以順勢問使用者要不要順便補一個測試案例。

### 6. 交付前總結

簡短說明:跑了什麼範圍的測試、結果如何、如果修了東西,是修了什麼原因造成的失敗。這段內容可以直接對應到`writeup.md`裡「How to run」或「Before vs. after」的驗證段落。
