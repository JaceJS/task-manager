# API contract

Base URL `http://localhost:8000/api`. Request and response bodies are JSON with `camelCase`
fields. The same contract is browsable as Swagger UI at http://localhost:8000/docs.

Every example below is real output from `curl` against a running backend.

## Response shape

Every response that has a body looks the same. On errors `data` is `null`, so a client
handles every failure in one place:

```
{ "message": "Board created", "data": { ... } }
{ "message": "Board 999 was not found", "data": null }
```

| Status | When                                                                            |
| ------ | ------------------------------------------------------------------------------- |
| 200    | Read, update or restore succeeded                                               |
| 201    | Created                                                                         |
| 204    | Deleted, no body                                                                |
| 400    | The body is not valid JSON                                                      |
| 422    | Valid JSON, invalid content: blank name, unknown status, extra field, wrong type |
| 404    | The board or task does not exist where the request looks for it (active, or in trash) |
| 409    | Conflicts with current data: name already used, board still has tasks, board in trash |
| 500    | Unexpected fault. Message: `Something went wrong on the server`                 |

## Endpoints

| Method   | Path                              | Does                                   |
| -------- | --------------------------------- | -------------------------------------- |
| `GET`    | `/api/boards`                     | List active boards                     |
| `POST`   | `/api/boards`                     | Create a board                         |
| `PATCH`  | `/api/boards/{boardId}`           | Rename a board                         |
| `DELETE` | `/api/boards/{boardId}`           | Move a board to trash                  |
| `GET`    | `/api/boards/{boardId}/tasks`     | List a board's tasks, optional `?status=` |
| `POST`   | `/api/boards/{boardId}/tasks`     | Create a task                          |
| `PATCH`  | `/api/tasks/{taskId}`             | Change status, title or description    |
| `DELETE` | `/api/tasks/{taskId}`             | Move a task to trash                   |
| `GET`    | `/api/trash/boards`               | List boards in trash                   |
| `GET`    | `/api/trash/tasks`                | List tasks in trash                    |
| `POST`   | `/api/boards/{boardId}/restore`   | Bring a board back from trash          |
| `POST`   | `/api/tasks/{taskId}/restore`     | Bring a task back from trash           |
| `DELETE` | `/api/trash/boards/{boardId}`     | Delete a board permanently             |
| `DELETE` | `/api/trash/tasks/{taskId}`       | Delete a task permanently              |

Path ids are integers; anything else is a 422:

```
GET /api/boards/abc/tasks
422 { "message": "path.board_id: Input should be a valid integer, unable to parse string as an integer", "data": null }
```

## Boards

### `GET /api/boards`

Active boards, newest first.

```
200 { "message": "Boards retrieved",
      "data": [ { "id": 1, "name": "Q4 Campaign",
                  "createdAt": "2026-09-18T06:48:48.917691Z", "updatedAt": "2026-09-18T06:48:48.917691Z" } ] }
```

### `POST /api/boards`

Body `{ "name": string }`. The name is trimmed, must be 1 to 255 characters, and must be unique
among active boards, ignoring case.

```
request  { "name": "Q4 Campaign" }
201      { "message": "Board created",
           "data": { "id": 1, "name": "Q4 Campaign", "createdAt": "2026-09-18T06:48:48.917691Z", "updatedAt": "2026-09-18T06:48:48.917691Z" } }
409      { "message": "A board named 'q4 campaign' already exists", "data": null }   (name "  q4 campaign ")
422      { "message": "Name must not be empty", "data": null }                      (name "   ")
400      { "message": "Request body is not valid JSON", "data": null }              (body {"name":)
```

### `PATCH /api/boards/{boardId}`

Rename. Body `{ "name": string }`, same rules as creating. A board may change only the case of
its own name.

```
request  { "name": "Q4 Campaign Launch" }
200      { "message": "Board renamed",
           "data": { "id": 1, "name": "Q4 Campaign Launch", "createdAt": "2026-09-18T06:48:48.917691Z", "updatedAt": "2026-09-18T06:48:48.994661Z" } }
409      { "message": "A board named 'onboarding' already exists", "data": null }   (another board is "Onboarding")
404      { "message": "Board 999 was not found", "data": null }
```

### `DELETE /api/boards/{boardId}`

Moves the board to trash (soft delete). Refused while it has active tasks; the database enforces
this too, with a trigger.

```
204      (no body)
409      { "message": "Board still has 1 task. Delete it first.", "data": null }
404      { "message": "Board 999 was not found", "data": null }
```

## Tasks

### `GET /api/boards/{boardId}/tasks`

Active tasks of an active board, newest first. Optional query `status` = `TODO` |
`IN_PROGRESS` | `DONE`. An empty board returns `"data": []`.

```
GET /api/boards/1/tasks?status=TODO
200 { "message": "Tasks retrieved",
      "data": [ { "id": 1, "boardId": 1, "title": "Draft the brief", "description": "Goals, audience and budget.",
                  "status": "TODO", "createdAt": "2026-09-18T06:48:49.048782Z", "updatedAt": "2026-09-18T06:48:49.048782Z" } ] }

GET /api/boards/1/tasks?status=DOING
422 { "message": "status: Input should be 'TODO', 'IN_PROGRESS' or 'DONE'", "data": null }
```

### `POST /api/boards/{boardId}/tasks`

Body `{ "title": string, "description"?: string | null }`. Title trimmed, 1 to 255 characters.
Status always starts as `TODO`.

```
request  { "title": "Draft the brief", "description": "Goals, audience and budget." }
201      { "message": "Task created",
           "data": { "id": 1, "boardId": 1, "title": "Draft the brief", "description": "Goals, audience and budget.",
                     "status": "TODO", "createdAt": "2026-09-18T06:48:49.048782Z", "updatedAt": "2026-09-18T06:48:49.048782Z" } }
422      { "message": "Title must not be empty", "data": null }
404      { "message": "Board 999 was not found", "data": null }
```

### `PATCH /api/tasks/{taskId}`

Change any of `status`, `title`, `description`. Only the fields sent are changed. `title` follows
the creation rules; `"description": null` or `""` clears the description.

```
request  { "status": "IN_PROGRESS" }
200      { "message": "Task updated",
           "data": { "id": 1, "boardId": 1, "title": "Draft the brief", "description": "Goals, audience and budget.",
                     "status": "IN_PROGRESS", "createdAt": "2026-09-18T06:48:49.048782Z", "updatedAt": "2026-09-18T06:48:49.140590Z" } }
422      { "message": "status: Input should be 'TODO', 'IN_PROGRESS' or 'DONE'", "data": null }   (status "FINISHED")
422      { "message": "Provide at least one field to update", "data": null }                      (body {})
422      { "message": "priority: Extra inputs are not permitted", "data": null }                   (unknown field)
404      { "message": "Task 999 was not found", "data": null }
```

### `DELETE /api/tasks/{taskId}`

Moves the task to trash (soft delete).

```
204      (no body)
404      { "message": "Task 1 was not found", "data": null }   (already in trash)
```

## Trash

Rows in trash have `deleted_at` set. They are invisible to every endpoint above and can be
restored or deleted permanently here.

### `GET /api/trash/boards`

Boards in trash, most recently deleted first.

```
200 { "message": "Boards in trash retrieved",
      "data": [ { "id": 1, "name": "Q4 Campaign Launch", "createdAt": "2026-09-18T06:48:48.917691Z",
                  "updatedAt": "2026-09-18T06:48:49.257653Z", "deletedAt": "2026-09-18T06:48:49.257653Z" } ] }
```

### `GET /api/trash/tasks`

Tasks in trash, most recently deleted first, with the name of their board.

```
200 { "message": "Tasks in trash retrieved",
      "data": [ { "id": 1, "boardId": 1, "title": "Draft the brief", "description": "Goals, audience and budget.",
                  "status": "IN_PROGRESS", "createdAt": "2026-09-18T06:48:49.048782Z", "updatedAt": "2026-09-18T06:48:49.224980Z",
                  "boardName": "Q4 Campaign Launch", "deletedAt": "2026-09-18T06:48:49.224980Z" } ] }
```

### `POST /api/boards/{boardId}/restore`

No body. Refused if an active board has taken the name in the meantime.

```
200      { "message": "Board restored",
           "data": { "id": 1, "name": "Q4 Campaign Launch", "createdAt": "2026-09-18T06:48:48.917691Z", "updatedAt": "2026-09-18T06:48:49.338390Z" } }
409      { "message": "A board named 'Q4 Campaign Launch' already exists. Rename it first.", "data": null }
404      { "message": "Board 2 was not found in trash", "data": null }
```

### `POST /api/tasks/{taskId}/restore`

No body. The task's board has to be active; the database enforces this too, with a trigger.

```
200      { "message": "Task restored",
           "data": { "id": 1, "boardId": 1, "title": "Draft the brief", "description": "Goals, audience and budget.",
                     "status": "IN_PROGRESS", "createdAt": "2026-09-18T06:48:49.048782Z", "updatedAt": "2026-09-18T06:48:49.356253Z" } }
409      { "message": "Restore the board 'Q4 Campaign Launch' first", "data": null }
404      { "message": "Task 1 was not found in trash", "data": null }   (the task is active)
```

### `DELETE /api/trash/boards/{boardId}`

Deletes the row for good. Refused while any of the board's tasks remain, even in trash;
`ON DELETE RESTRICT` on the foreign key enforces this in the database.

```
204      (no body)
409      { "message": "Board still has 1 task in trash. Delete it permanently first.", "data": null }
404      { "message": "Board 1 was not found in trash", "data": null }
```

### `DELETE /api/trash/tasks/{taskId}`

Deletes the row for good. Only tasks already in trash.

```
204      (no body)
404      { "message": "Task 1 was not found in trash", "data": null }
```
