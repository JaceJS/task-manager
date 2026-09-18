# Task Manager

A small task management app. You create boards, add tasks to a board, move each task through
`TODO`, `IN_PROGRESS` and `DONE`, filter by status, and delete what you no longer need. Deleted
boards and tasks go to a Trash page, where they can be restored or deleted permanently.

It is two separate services that only talk over HTTP:

```
browser ──> frontend (React, :5173) ──REST/JSON──> backend (FastAPI, :8000) ──> PostgreSQL (:5432, Docker)
```

| Part     | Folder                   | README                                     |
| -------- | ------------------------ | ------------------------------------------ |
| Backend  | [`backend/`](backend/)   | [backend/README.md](backend/README.md): setup, tests. [backend/API.md](backend/API.md): API contract |
| Frontend | [`frontend/`](frontend/) | [frontend/README.md](frontend/README.md): setup, structure, UI states |
| Database | [`docs/SCHEMA.md`](docs/SCHEMA.md) | Tables, constraints, indexes and why |

## Prerequisites

| Tool                    | Version                    | Checked with            |
| ----------------------- | -------------------------- | ----------------------- |
| Docker with Compose v2  | any recent                 | Docker 28.3, Compose 2.38 |
| Python                  | 3.11 or newer              | 3.14.4                  |
| Node.js                 | 20.19+ or 22.12+ (Vite 8)  | 22.17.1, npm 10.9       |

Everything is free and runs locally. No accounts or keys are needed.

## Quick start from a clean clone

Ports 5432, 8000 and 5173 must be free. Use three terminals, each starting in the repository
root (`task-manager/`).

**1. Database**

```bash
git clone https://github.com/JaceJS/task-manager.git task-manager
cd task-manager
docker compose up -d db
```

**2. Backend** (http://localhost:8000, interactive API docs at http://localhost:8000/docs)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head               # creates the schema in the empty database
uvicorn app.main:app --reload --port 8000
```

**3. Frontend** (http://localhost:5173)

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173, create a board and add tasks.

**Tests** (backend, with the database from step 1 running):

```bash
cd backend && source .venv/bin/activate && pytest -v
```

Expected: `55 passed`. The test database is created automatically.
Details in [backend/README.md](backend/README.md#tests).

## Stack and why

- **Backend:** Python, FastAPI, SQLAlchemy 2, Alembic. **Database:** PostgreSQL 16 in Docker.
  The reasons are in [backend/README.md](backend/README.md#stack-choice).
- **Frontend:** React 19 with Vite, TypeScript and Tailwind, because the brief requires React
  and Vite gives a fast, separate dev server with typed code and no component library to learn.

## Assumptions

Where the brief was silent, these were decided:

| #   | Question                                   | Decision                                                        |
| --- | ------------------------------------------ | --------------------------------------------------------------- |
| 1   | What happens to tasks when a board is deleted? | Deleting is refused while the board has active tasks (409). Delete the tasks first |
| 2   | Can a task's title and description change? | Yes, with the same rules as creating one                        |
| 3   | Can two boards share a name?               | No. Names are unique among active boards, ignoring case         |
| 4   | Maximum length?                            | 255 characters for board names and task titles. Descriptions are unlimited |
| 5   | Leading and trailing spaces?               | Trimmed. A value made only of spaces counts as empty and is rejected |
| 6   | Order of lists?                            | Newest first, for boards and tasks                              |
| 7   | Filtering by an unknown status?            | Rejected with 422 and a message                                 |
| 8   | Can a board be deleted from the UI?        | Yes, after a confirmation dialog                                |
| 9   | Is a new board selected after creating it? | Yes                                                             |
| 10  | Frontend tests?                            | Skipped. The brief makes them optional                          |
| 11  | Is a delete final?                         | No. `DELETE` moves the row to trash (`deleted_at`). It can be restored or deleted permanently from the Trash page |
| 12  | Can a board be renamed?                    | Yes, with the same rules as creating one                        |
| 13  | Restoring a board whose name was taken meanwhile? | Refused (409). Rename the active board first            |
| 14  | Restoring a task whose board is in trash?  | Refused (409). Restore the board first                          |
| 15  | Deleting a board permanently while its tasks are in trash? | Refused (409). Delete those tasks permanently first |
| 16  | Language?                                  | English, in the UI and in every API message                     |

## Trade-offs

- **Soft delete with a Trash page instead of a hard delete.** A mistaken delete can be undone,
  at the cost of a `deleted_at IS NULL` filter on every query, a partial unique index, and six
  more endpoints.
- **Database-enforced delete rules.** A trigger refuses to move a board with active tasks to
  trash, and `ON DELETE RESTRICT` refuses to remove a board that still has task rows. The
  service checks first only to return a clear message. The rule holds even for SQL run by hand.
- **Status as `varchar` + `CHECK`, not a native enum.** Explained in
  [docs/SCHEMA.md](docs/SCHEMA.md#a-decision-considered-and-rejected).
- **Refetch after every change** instead of keeping a client-side cache in sync. One extra
  request, but the screen always matches the server. The reply to the change is shown at once so
  nothing flashes back meanwhile.

Frontend-only decisions (Kanban columns, filtering on screen, no drag and drop) are in
[frontend/README.md](frontend/README.md#decisions). Known issues for each service are listed
in its own README.

## Optional extras

From the brief's optional list, two are done: **editing a task's title and description** (API
and UI), and **counts per status** (column headers, filter chips and a status bar). The
one-command `docker compose up` for all services is not done.

Beyond the brief, two features were added because a real user needs them once deleting is
possible: **renaming a board**, and a **Trash page** to restore or permanently delete boards
and tasks. Both follow the same rules as the core: tested in the service layer, documented in
[backend/API.md](backend/API.md), and guarded by the database.

## Unfinished work

Nothing from the brief's required list is unfinished. The optional items that were not done
are listed above: the one-command `docker compose up`, and frontend tests (assumption 10).

## Repository layout

```
task-manager/
  docker-compose.yml   PostgreSQL 16 for development and tests
  docs/SCHEMA.md       database design
  backend/             FastAPI service, feature modules: boards, tasks
  frontend/            React app, feature folders: boards, tasks, trash
```
