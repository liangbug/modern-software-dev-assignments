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
### Automation #1
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


### Automation #2 — Six-role SubAgent pipeline (Plan → DB → Refactor → Test → Code → Docs)
a. Design inspiration (e.g. cite the best-practices and/or sub-agents docs)
> Based on the SubAgents overview (docs.anthropic.com/en/docs/claude-code/sub-agents) and `assignment.md`
> section C's three example flows (TestAgent+CodeAgent, DocsAgent+CodeAgent, DBAgent+RefactorAgent). Instead
> of building three unrelated demo pairs, I combined all three into a single ordered pipeline and added a
> sixth role, `plan-agent`, at the front to produce shared planning docs the other five read from — this
> follows the best-practices doc's guidance to keep each subagent's context and responsibility narrow
> ("role-specialized"), and to use checklists/scratchpads to hand off between roles rather than relying on
> implicit shared state.

b. Design of each automation, including goals, inputs/outputs, steps
> Six SubAgent definitions live at `week4/.claude/agents/{plan-agent,db-agent,refactor-agent,test-agent,
> code-agent,doc-agent}.md` (flat files, frontmatter `name`/`description`/`tools`). Each has a hard
> file-scope boundary so responsibilities don't overlap:
> - **plan-agent** — reads a `docs/TASKS.md` item, writes `docs/plans/<task-slug>/{design.md,tasks.md,
>   testing.md}` (implementation plan, per-role task checklist, given/when/then test scenarios). Touches
>   only `docs/plans/`.
> - **db-agent** — reads `design.md`'s schema section, edits only `backend/app/models.py` +
>   `data/seed.sql` (and, if it chooses the auto-migration option, `backend/app/db.py`). Must document
>   rollback/compatibility notes for existing `data/app.db` files.
> - **refactor-agent** — applies the resulting field to `backend/app/schemas.py` / router signatures
>   (structural only, no business logic), then runs `make format && make lint`.
> - **test-agent** — writes/edits only `backend/tests/`, either (a) writing new failing tests from
>   `testing.md`, or (b) running `make test` to verify and reporting pass/fail with concrete assertion
>   diffs. Never touches `backend/app/`.
> - **code-agent** — implements only in `backend/app/` to turn test-agent's failing tests green, then
>   self-checks with `make test` + `make format && make lint`.
> - **doc-agent** — updates only `docs/API.md` and `docs/TASKS.md` (checked-off items) after tests are
>   green, and flags `writeup.md` sections to fill in — never touches code.
> Ordering is dependency-driven, not arbitrary: schema must exist before models can be tested; structure
> must be applied before tests can even collect; tests are written (TDD) before implementation; docs are
> written last since they describe the final, settled state.

c. How to run it (exact commands), expected outputs, and rollback/safety notes
> In an interactive Claude Code session (where custom subagents in `.claude/agents/` are live-loaded),
> invoke each role in order, e.g. `@plan-agent 規劃 docs/TASKS.md 第4項...` then `@db-agent ...` etc., or
> let Claude auto-delegate via each agent's `description` trigger text. After each step, run
> `make test`/`make lint` (in `week4/`) to confirm the expected red→green transition.
> Rollback/safety note (written by db-agent for this run): SQLite's `Base.metadata.create_all` never
> `ALTER TABLE`s an existing table, so a locally-existing `data/app.db` created before this change will
> throw `OperationalError: no such column: notes.tags` on any query touching the new column. This repo has
> no migration tooling and no real data, so the documented rollback is: delete `data/app.db` and re-run
> `make run`/`make seed` to rebuild it with the new schema. Tests are unaffected — `backend/tests/
> conftest.py`'s `client` fixture always uses a fresh temp DB.

d. Before vs. after (i.e. manual workflow vs. automated workflow)
> Before: a single change spanning schema + business logic + tests + docs meant manually round-tripping
> between `models.py`, `schemas.py`, `routers/`, `services/`, `backend/tests/`, and `docs/` in one long,
> unstructured session — easy to lose track of which file was "settled" vs. still in flux, and docs
> updates often got skipped or written before the API shape was final (immediate drift).
> After: the same change is split into six bounded steps with an explicit hand-off artifact between them
> (`design.md`/`tasks.md`/`testing.md`, then git-visible diffs per role). Each step has a narrow, checkable
> scope ("did db-agent only touch models.py and seed.sql?"), and docs are guaranteed to come last, after
> tests are green, so `API.md`/`TASKS.md` describe the actual shipped behavior instead of an in-progress
> guess.

e. How you used the automation to enhance the starter application
> Ran the full six-step pipeline once against `docs/TASKS.md` item 4 ("Improve extraction logic"): added a
> `tags` column to `Note` (db-agent), wired it into `NoteRead` (refactor-agent), wrote 8 new tests covering
> `extract_tags` parsing rules and the `/notes/` create+read round-trip (test-agent), implemented
> `extract_tags()` in `services/extract.py` and wired it into `POST /notes/` (code-agent), re-verified all
> 11 tests green + lint clean (test-agent), and documented the new `tags` field in a newly-created
> `docs/API.md` plus checked off the corresponding `docs/TASKS.md` bullets (doc-agent). The planning
> artifacts are kept at `docs/plans/note-tags/` as evidence of the run.


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
