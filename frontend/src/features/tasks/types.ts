export const TASK_STATUSES = ['TODO', 'IN_PROGRESS', 'DONE'] as const

export type TaskStatus = (typeof TASK_STATUSES)[number]

export const STATUS_LABELS: Record<TaskStatus, string> = {
  TODO: 'To do',
  IN_PROGRESS: 'In progress',
  DONE: 'Done',
}

export const STATUS_STYLE: Record<
  TaskStatus,
  { dot: string; pill: string; column: string }
> = {
  TODO: {
    dot: 'bg-todo',
    pill: 'bg-todo-tint text-todo-ink border-todo/30',
    column: 'border-t-todo',
  },
  IN_PROGRESS: {
    dot: 'bg-progress',
    pill: 'bg-progress-tint text-progress-ink border-progress/30',
    column: 'border-t-progress',
  },
  DONE: {
    dot: 'bg-done',
    pill: 'bg-done-tint text-done-ink border-done/30',
    column: 'border-t-done',
  },
}

export type StatusCounts = Record<TaskStatus, number>

export function countByStatus(tasks: readonly { status: TaskStatus }[]): StatusCounts {
  const counts: StatusCounts = { TODO: 0, IN_PROGRESS: 0, DONE: 0 }
  for (const task of tasks) counts[task.status] += 1
  return counts
}

export interface Task {
  id: number
  boardId: number
  title: string
  description: string | null
  status: TaskStatus
  createdAt: string
  updatedAt: string
}

export interface TaskDraft {
  title: string
  description: string
}
