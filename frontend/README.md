# Frontend

React 19 app for the task manager. Vite, TypeScript, Tailwind CSS 4.
Runs on http://localhost:5173 and talks to the backend only over HTTP.

## Setup and run

Needs Node.js 20.19+ or 22.12+ (required by Vite 8). For data, the backend should run on port
8000. Without it the app still loads and shows a "Can't reach the server" message.

```bash
cd frontend
npm install
npm run dev          # http://localhost:5173
```

| Command           | Does                                        |
| ----------------- | ------------------------------------------- |
| `npm run dev`     | Development server with hot reload          |
| `npm run build`   | Type check (`tsc -b`) and production build into `dist/` |
| `npm run preview` | Serve the production build locally          |
| `npm run lint`    | Lint with oxlint                            |

### Backend address

The backend URL comes from `VITE_API_BASE_URL` and defaults to `http://localhost:8000`, so no
`.env` is needed for the standard setup. To point at another backend:

```bash
cp .env.example .env     # then edit VITE_API_BASE_URL
```

The backend only accepts requests from `http://localhost:5173` (CORS), so keep that port.

## What the screen does

- A sidebar lists boards, newest first. **New board** creates one and selects it. **Rename**
  in the board header edits the name in place (Enter saves, Escape cancels).
- The selected board is shown as three columns: **To do**, **In progress**, **Done**, each
  with its count. A bar under the board name shows the share of each status.
- **Add task** at the top of To do opens a form: Enter saves, Escape cancels. The form stays
  open for the next task.
- Each card shows title, description, status and created time. The coloured status pill is a
  dropdown; changing it moves the card to the matching column. Edit and delete icons appear on
  hover or keyboard focus. On screens without hover they are meant to stay visible (a CSS
  media query; not tried on a real touch device).
- Filter chips (**All**, **To do**, **In progress**, **Done**) show only the chosen column.
- Deleting a task or a board asks for confirmation, then moves it to trash. A board that still
  has tasks is not moved; the API's reason is shown.
- **Trash** (bottom of the sidebar) lists deleted boards and tasks with the time they were
  deleted. Each can be **restored** or **deleted permanently** (after a confirmation that says
  it cannot be undone). When a rule blocks the action, such as restoring a task whose board is
  still in trash, the API's reason is shown.

### States other than the happy path

| State                   | What the user sees                                                  |
| ----------------------- | ------------------------------------------------------------------- |
| Loading                 | Grey placeholder blocks. After a change, the current cards stay while the list refreshes |
| Backend not running     | "Can't reach the server at http://localhost:8000. Check that the backend is running, then try again." with **Try again**. Never a blank page |
| Request rejected        | The API's `message`, next to the form or as a banner                 |
| No boards yet           | "No boards yet. Create your first board to start adding tasks."     |
| Board with no tasks     | "No tasks yet. Add the first one above." and an empty note per column |
| Blank title or name     | Rejected in the browser before sending ("Title must not be empty")  |
| Trash is empty          | "Trash is empty.", or "No boards in trash." / "No tasks in trash." per section |

## Structure

```
src/
  main.tsx, App.tsx       entry point; App lays out the screen and holds the view (board or Trash),
                          the selected board and the filter
  index.css               design tokens (colours, font) in one place
  shared/
    apiClient.ts          the only file that calls fetch; turns every failure into one error type
    Button.tsx, icons.tsx one button style, four inline SVG icons
    formatDateTime.ts     one date format for the whole app
    ConfirmDialog.tsx     confirmation built on the native <dialog> element
    LoadingState.tsx, ErrorState.tsx, EmptyState.tsx
  features/
    boards/               api.ts, useBoards.ts, BoardList, BoardForm (create and rename), BoardHeader
    tasks/                api.ts, useTasks.ts, TaskList (columns), TaskItem (card), TaskForm,
                          TaskStatusSelect, TaskStatusFilter, types.ts (statuses and their colours)
    trash/                api.ts, useTrash.ts, TrashPage, types.ts
```

Data always flows one way: `shared/apiClient.ts` → `features/<x>/api.ts` → `use<X>.ts` hook →
components. Only the two screens call the data hooks: `App` (`useBoards`, `useTasks`) and
`TrashPage` (`useTrash`).
Every other component gets data and callbacks as props; at most it keeps UI state such as
"is this form open".

## Decisions

- **Kanban columns**, the layout used by Trello, Jira, Linear and GitHub Projects, so it needs
  no explanation. Colour is saved for the three statuses; everything else stays neutral.
- **The status filter runs on screen.** The board loads all its tasks once, because the
  columns, chips and bar need the count of every status at the same time. The backend's
  `?status=` filter stays available and tested for API clients.
- **Refetch after every change**, so the screen always matches the database, including
  ordering. The server's reply to the change itself is applied at once (a moved card, a removed
  row), so nothing flashes back while the refetch runs.
- **Buttons wait for their request.** The status dropdown and the Restore button are disabled
  until their request finishes, so a double click cannot send the same change twice.
- **No drag and drop.** Moving a card is done with the status dropdown, which works with a
  keyboard and on touch screens. Drag and drop that does both needs an extra library.
- **No component library.** Tailwind plus a few small shared components. The only extra
  package is the Plus Jakarta Sans font, bundled with the app so it also works offline.

## Tests

There are no frontend tests; the brief makes them optional and the time went to backend tests.
Every state and flow above was checked in a Chromium browser (driven with Playwright) at
desktop (1280 px) and phone (390 px) widths, including stopping the backend, reloading the
page, then starting the backend again and pressing **Try again**.

## Known issues

- If the backend returns an unexpected 500, the browser reports it as a network error,
  because that response has no CORS headers (see the backend README).
