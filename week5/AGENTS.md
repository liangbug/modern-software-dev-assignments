# week5-repo-rules

## Tech Stack
- Backend: FastAPI
- ORM: SQLAlchemy
- Database: SQLite

## Code Architecture
- Routers (路由): `backend/app/routers/`
- Schemas (結構): `backend/app/schemas.py`
- Models (模型): `backend/app/models.py`

## Commands
- Test runner (測試): `week5-test-runner`
- Docs sync (文檔同步): `week5-docs-sync`
- Refactor tool (重構工具): `week5-refactor-harness`

## Rules & Boundaries

### Always Do
- 改完程式碼後，必須執行 `week5-test-runner` 進行自動測試確認，不可僅憑肉眼判斷。
- 新增或修改 API 行為時，必須同步更新 `backend/tests/` 中對應的測試，並在完成後執行 `week5-docs-sync` 以保持 `docs/API.md` 的即時同步。
- 保持現有的 `response_model` 風格，並與既有的程式碼命名慣例完全一致。

### Never Do
- 調整檔案結構或重新命名時，禁止手動修改，必須改用 `week5-refactor-harness` 來進行。
