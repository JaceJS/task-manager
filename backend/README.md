# Backend

REST API for boards and tasks. FastAPI, SQLAlchemy 2, Alembic, PostgreSQL 16.
Runs on http://localhost:8000. Interactive docs (Swagger UI) at http://localhost:8000/docs.

## Stack choice

Python with FastAPI, because it is my strongest language and FastAPI's typed request models give
input validation and an OpenAPI page for free, while keeping the HTTP layer thin enough that
the business rules sit in plain service classes that are unit tested without a server.
PostgreSQL 16 (in Docker), because the brief prefers it and every rule that matters here, the
foreign key, the check constraints, a case-insensitive partial unique index and the delete
triggers, is enforced by the database itself. SQLAlchemy 2 and Alembic are the standard ORM and
migration tool for that pair.

## Prerequisites

| Tool                   | Version       | Checked with               |
| ---------------------- | ------------- | -------------------------- |
| Python                 | 3.11 or newer | 3.14.4                     |
| Docker with Compose v2 | any recent    | Docker 28.3, Compose 2.38  |

Ports 5432 (database) and 8000 (API) must be free. Nothing needs an account or a licence.

## Setup and run

From the repository root, start PostgreSQL 16 (defined in `../docker-compose.yml`):

```bash
docker compose up -d db
```

Then, in `backend/`:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

The API is now at http://localhost:8000 (try `curl http://localhost:8000/api/boards`).
The frontend is not needed for any of this.

`.env` holds a single setting, `DATABASE_URL`. The example value matches `docker-compose.yml`.

### From an empty database to a running app

`alembic upgrade head` runs the migrations in `alembic/versions/` and creates both tables, their
constraints, indexes and triggers. Nothing else is needed: the app starts with no boards. The
first migration is written by hand, because Alembic does not detect triggers and handles partial
and expression indexes poorly. The schema itself is described in [../docs/SCHEMA.md](../docs/SCHEMA.md).

Data lives in the Docker volume `pgdata`, so it survives restarts of the backend and of the
container. `docker compose down -v` removes it.

## Tests

With the database container running and the virtualenv active:

```bash
pytest -v
```

Expected result: `55 passed, 2 warnings` (the warnings are explained under Known issues).

- The tests use a real PostgreSQL database, `taskmanager_test`, which `tests/conftest.py`
  creates on the first run and migrates with `alembic upgrade head`. SQLite was not used
  because the rules under test (foreign key, check constraints, triggers) only exist in
  PostgreSQL.
- Each test runs inside a transaction that is rolled back, so tests do not affect each other
  or the development data.
- If PostgreSQL is not reachable, pytest stops with: `Start it first with: docker compose up -d db`.

| File                                   | What it proves                                                   |
| -------------------------------------- | ---------------------------------------------------------------- |
| `tests/boards/test_board_service.py`   | Board rules: trimming, blank and too-long names, unique names ignoring case, delete refused while tasks exist, reusing the name of a deleted board |
| `tests/boards/test_board_rename.py`    | Rename: new name and `updated_at`, blank name, a name another board uses, unknown or trashed board, changing only the case of its own name |
| `tests/boards/test_board_trash.py`     | Boards in trash: listing order, restore, restore refused when the name is taken, permanent delete, permanent delete refused while tasks remain, active boards cannot be deleted permanently |
| `tests/tasks/test_task_service.py`     | Task rules: default status and trimming, blank and too-long titles, unknown board or task, filter by status (and an invalid one), empty board, invalid status, update with no fields, a task in trash can no longer be changed |
| `tests/tasks/test_task_trash.py`       | Tasks in trash: listing with board name, restore, restore refused while the board is in trash, permanent delete, active tasks cannot be deleted permanently |
| `tests/test_database_rules.py`         | The database itself refuses a fake `board_id`, a hard delete of a board with tasks, trashing a board with active tasks, and an active task on a trashed board. Plain SQL, no app code |
| `tests/test_api_errors.py`             | Through HTTP: malformed JSON gives 400, a blank name 422, an unknown board 404, all in the same `{message, data: null}` shape |

Services are tested directly, without starting a web server.

## Structure

A modular structure organised by feature. Each feature module keeps the same layers.

```
app/
  main.py                 app, CORS, routers, error handlers
  core/                   shared: settings, database session, base schema, errors, text validation
  modules/
    boards/               router.py service.py repository.py schemas.py models.py exceptions.py
    tasks/                (same files)
```

| Layer        | Does                                              | Does not                           |
| ------------ | ------------------------------------------------- | ---------------------------------- |
| `router`     | Reads the request, calls the service, wraps the response. Each module also has a `trash_router` for `/api/trash/...` | Business rules |
| `service`    | Business rules, validation, transactions           | Know about HTTP or status codes    |
| `repository` | Queries. Queries for active data filter out rows in trash; the `*_trashed` ones read only the trash | Business rules |
| `models`     | Table mapping                                      |                                    |

Services raise their own exceptions (`BoardNotFound`, `BoardNameTaken`, ...). The only place
that turns them into status codes is `app/core/error_handlers.py`.

## API contract

All 14 endpoints, with a request, a success response and error responses for each, are in
**[API.md](API.md)**. In short:

- Every response with a body is `{ "message": ..., "data": ... }`; on errors `data` is `null`.
- 200 read or update, 201 create, 204 delete, 400 body is not JSON, 422 invalid content,
  404 not found, 409 conflicts with current data, 500 only for an unexpected fault.
- `DELETE` moves a board or task to trash. The `/api/trash/...` endpoints list, restore and
  delete permanently.

## Known issues

- **Two deprecation warnings in the test output**, both from inside Starlette's `TestClient`:
  it suggests `httpx2` instead of `httpx`, and it uses a deprecated `anyio` alias. Neither
  comes from this project's code, and all tests pass.
- **A 500 response carries no CORS headers.** Starlette's error middleware sits outside the CORS
  middleware, so in the browser an unexpected server fault looks like a network error instead
  of showing the 500 message. `curl` sees the proper body.
- **CORS allows only `http://localhost:5173`.** Running the frontend on another port needs a
  change to `FRONTEND_ORIGIN` in `app/main.py`.
- **Checked on Python 3.14.4 only.** The code needs 3.11+ (it uses `StrEnum`), and every pinned
  package declares support for 3.10 or newer, but other versions were not run.
- **Validation messages are raw for type errors.** Business rules return plain sentences
  (`Name must not be empty`); type and format errors return Pydantic's text prefixed with the
  field (`path.board_id: Input should be a valid integer...`).
