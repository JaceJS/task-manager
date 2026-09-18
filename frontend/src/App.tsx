import { useState } from 'react'

import { NewBoardForm } from './features/boards/BoardForm'
import { BoardHeader } from './features/boards/BoardHeader'
import { BoardList } from './features/boards/BoardList'
import { useBoards } from './features/boards/useBoards'
import { TaskList } from './features/tasks/TaskList'
import { StatusBar, TaskStatusFilter } from './features/tasks/TaskStatusFilter'
import {
  STATUS_STYLE,
  TASK_STATUSES,
  countByStatus,
  type Task,
  type TaskStatus,
} from './features/tasks/types'
import { useTasks } from './features/tasks/useTasks'
import { TrashPage } from './features/trash/TrashPage'
import { ConfirmDialog, type ConfirmRequest } from './shared/ConfirmDialog'
import { EmptyState } from './shared/EmptyState'
import { ErrorState } from './shared/ErrorState'
import { LoadingState } from './shared/LoadingState'
import { TrashIcon } from './shared/icons'
import { useActionError } from './shared/useActionError'

type View = 'boards' | 'trash'

export default function App() {
  const [view, setView] = useState<View>('boards')
  const [selectedBoardId, setSelectedBoardId] = useState<number | null>(null)
  const [statusFilter, setStatusFilter] = useState<TaskStatus | null>(null)
  const [confirmRequest, setConfirmRequest] = useState<ConfirmRequest | null>(null)

  const boards = useBoards()
  const action = useActionError()

  const selectedBoard =
    boards.boards.find((board) => board.id === selectedBoardId) ?? boards.boards[0] ?? null
  const tasks = useTasks(selectedBoard?.id ?? null)
  const counts = countByStatus(tasks.tasks)

  const selectBoard = (boardId: number) => {
    setSelectedBoardId(boardId)
    setStatusFilter(null)
    action.clear()
    setView('boards')
  }

  const askDeleteBoard = () => {
    if (!selectedBoard) return
    setConfirmRequest({
      title: `Move '${selectedBoard.name}' to trash?`,
      body: 'You can restore it from Trash. A board that still has tasks cannot be moved there.',
      confirmLabel: 'Move to trash',
      onConfirm: () => action.run(() => boards.deleteBoard(selectedBoard.id)),
    })
  }

  const askDeleteTask = (task: Task) => {
    setConfirmRequest({
      title: `Move '${task.title}' to trash?`,
      body: 'You can restore it from Trash.',
      confirmLabel: 'Move to trash',
      onConfirm: () => action.run(() => tasks.deleteTask(task.id)),
    })
  }

  return (
    <div className="flex min-h-screen flex-col md:flex-row">
      <aside className="shrink-0 border-b border-line bg-panel p-4 md:sticky md:top-0 md:h-screen md:w-64 md:overflow-y-auto md:border-r md:border-b-0">
        <p className="mb-5 flex items-center gap-2 px-2 text-sm font-bold">
          <span aria-hidden="true" className="flex gap-0.5">
            {TASK_STATUSES.map((status) => (
              <span key={status} className={`h-3.5 w-1.5 rounded-full ${STATUS_STYLE[status].dot}`} />
            ))}
          </span>
          Task Manager
        </p>

        <h2 className="mb-2 px-2 text-[11px] font-bold tracking-wider text-muted uppercase">
          Boards
        </h2>
        <div className="space-y-2">
          {boards.isLoading && <LoadingState label="Loading boards..." rows={3} />}
          {view === 'trash' && boards.error && (
            <ErrorState message="Boards could not be loaded." onRetry={boards.reload} />
          )}
          <BoardList
            boards={boards.boards}
            selectedBoardId={view === 'boards' ? (selectedBoard?.id ?? null) : null}
            onSelect={selectBoard}
          />
          <NewBoardForm
            onCreate={async (name) => {
              const board = await boards.createBoard(name)
              selectBoard(board.id)
            }}
          />
        </div>

        <div className="mt-4 border-t border-line pt-4">
          <button
            type="button"
            onClick={() => setView('trash')}
            aria-current={view === 'trash' ? 'page' : undefined}
            className={`flex w-full items-center gap-2 rounded-lg px-2 py-1.5 text-sm font-medium transition-colors ${
              view === 'trash'
                ? 'bg-surface text-ink'
                : 'text-muted hover:bg-surface hover:text-ink'
            }`}
          >
            <TrashIcon />
            Trash
          </button>
        </div>
      </aside>

      <main className="min-w-0 flex-1 space-y-5 p-4 md:p-8">
        {view === 'trash' ? (
          <TrashPage
            onConfirm={setConfirmRequest}
            onBoardRestored={() => boards.reload()}
            onTaskRestored={() => tasks.reload()}
          />
        ) : boards.error ? (
          <ErrorState message={boards.error} onRetry={boards.reload} />
        ) : !selectedBoard ? (
          !boards.isLoading && (
            <EmptyState message="No boards yet. Create your first board to start adding tasks." />
          )
        ) : (
          <>
            <BoardHeader
              key={selectedBoard.id}
              board={selectedBoard}
              onRename={(name) => boards.renameBoard(selectedBoard.id, name)}
              onDelete={askDeleteBoard}
            >
              <StatusBar counts={counts} />
            </BoardHeader>

            {action.error && <ErrorState message={action.error} />}

            <TaskStatusFilter counts={counts} value={statusFilter} onChange={setStatusFilter} />

            {tasks.isLoading && <LoadingState label="Loading tasks..." />}
            {tasks.error && <ErrorState message={tasks.error} onRetry={tasks.reload} />}
            {!tasks.isLoading && !tasks.error && (
              <TaskList
                tasks={tasks.tasks}
                statuses={statusFilter ? [statusFilter] : TASK_STATUSES}
                onCreate={({ title, description }) => tasks.createTask(title, description)}
                onChangeStatus={(taskId, status) =>
                  action.run(() => tasks.updateTask(taskId, { status }))
                }
                onSaveDetails={(taskId, draft) =>
                  tasks.updateTask(taskId, {
                    title: draft.title,
                    description: draft.description || null,
                  })
                }
                onDelete={askDeleteTask}
              />
            )}
          </>
        )}
      </main>

      <ConfirmDialog request={confirmRequest} onClose={() => setConfirmRequest(null)} />
    </div>
  )
}
