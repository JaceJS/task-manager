import { useState } from 'react'

import { EmptyState } from '../../shared/EmptyState'
import { PlusIcon } from '../../shared/icons'
import { TaskForm } from './TaskForm'
import { TaskItem } from './TaskItem'
import { STATUS_LABELS, STATUS_STYLE, type Task, type TaskDraft, type TaskStatus } from './types'

const EMPTY_COLUMN_TEXT: Record<TaskStatus, string> = {
  TODO: 'Nothing waiting to start.',
  IN_PROGRESS: 'Nothing in progress.',
  DONE: 'Nothing done yet.',
}

interface TaskListProps {
  tasks: Task[]
  statuses: readonly TaskStatus[]
  onCreate: (draft: TaskDraft) => Promise<unknown>
  onChangeStatus: (taskId: number, status: TaskStatus) => Promise<unknown>
  onSaveDetails: (taskId: number, draft: TaskDraft) => Promise<unknown>
  onDelete: (task: Task) => void
}

export function TaskList({
  tasks,
  statuses,
  onCreate,
  onChangeStatus,
  onSaveDetails,
  onDelete,
}: TaskListProps) {
  const layout = statuses.length === 1 ? 'max-w-xl' : 'md:grid-cols-3'

  return (
    <div className={`grid items-start gap-4 ${layout}`}>
      {statuses.map((status) => {
        const columnTasks = tasks.filter((task) => task.status === status)
        return (
          <section
            key={status}
            aria-label={STATUS_LABELS[status]}
            className={`rounded-2xl border-t-4 bg-panel/60 p-3 ring-1 ring-line ${STATUS_STYLE[status].column}`}
          >
            <header className="mb-3 flex items-center gap-2 px-1">
              <span className={`size-2.5 rounded-full ${STATUS_STYLE[status].dot}`} />
              <h2 className="text-xs font-bold tracking-wider text-ink uppercase">
                {STATUS_LABELS[status]}
              </h2>
              <span className="ml-auto rounded-full bg-surface px-2 font-mono text-xs text-muted">
                {columnTasks.length}
              </span>
            </header>

            {status === 'TODO' && <AddTask onCreate={onCreate} />}

            {columnTasks.length === 0 ? (
              <EmptyState
                compact
                message={
                  status === 'TODO' && tasks.length === 0
                    ? 'No tasks yet. Add the first one above.'
                    : EMPTY_COLUMN_TEXT[status]
                }
              />
            ) : (
              <ul className="space-y-2">
                {columnTasks.map((task) => (
                  <TaskItem
                    key={task.id}
                    task={task}
                    onChangeStatus={(next) => onChangeStatus(task.id, next)}
                    onSaveDetails={(draft) => onSaveDetails(task.id, draft)}
                    onDelete={() => onDelete(task)}
                  />
                ))}
              </ul>
            )}
          </section>
        )
      })}
    </div>
  )
}

function AddTask({ onCreate }: { onCreate: (draft: TaskDraft) => Promise<unknown> }) {
  const [isOpen, setIsOpen] = useState(false)

  if (isOpen) {
    return (
      <div className="mb-2 rounded-xl border border-line bg-panel p-3 shadow-sm">
        <TaskForm submitLabel="Add task" onSubmit={onCreate} onCancel={() => setIsOpen(false)} />
      </div>
    )
  }

  return (
    <button
      type="button"
      onClick={() => setIsOpen(true)}
      className="mb-2 flex w-full items-center gap-2 rounded-xl border border-dashed border-line px-3 py-2.5 text-sm font-medium text-muted transition-colors hover:border-todo hover:bg-todo-tint hover:text-todo-ink"
    >
      <PlusIcon />
      Add task
    </button>
  )
}
