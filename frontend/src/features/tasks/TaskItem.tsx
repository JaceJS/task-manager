import { useState } from 'react'

import { Button } from '../../shared/Button'
import { formatDateTime } from '../../shared/formatDateTime'
import { PencilIcon, TrashIcon } from '../../shared/icons'
import { TaskForm } from './TaskForm'
import { TaskStatusSelect } from './TaskStatusSelect'
import type { Task, TaskDraft, TaskStatus } from './types'

interface TaskItemProps {
  task: Task
  onChangeStatus: (status: TaskStatus) => Promise<unknown>
  onSaveDetails: (draft: TaskDraft) => Promise<unknown>
  onDelete: () => void
}

export function TaskItem({ task, onChangeStatus, onSaveDetails, onDelete }: TaskItemProps) {
  const [isEditing, setIsEditing] = useState(false)
  const [isSavingStatus, setIsSavingStatus] = useState(false)

  const changeStatus = async (status: TaskStatus) => {
    setIsSavingStatus(true)
    try {
      await onChangeStatus(status)
    } finally {
      setIsSavingStatus(false)
    }
  }

  return (
    <li className="group rounded-xl border border-line bg-panel p-3 shadow-sm transition-shadow hover:shadow-md">
      {isEditing ? (
        <TaskForm
          initial={{ title: task.title, description: task.description ?? '' }}
          submitLabel="Save"
          onCancel={() => setIsEditing(false)}
          onSubmit={async (draft) => {
            await onSaveDetails(draft)
            setIsEditing(false)
          }}
        />
      ) : (
        <>
          <div className="flex items-start justify-between gap-2">
            <h3 className="min-w-0 pt-1 text-sm font-semibold break-words">{task.title}</h3>
            <div className="-mt-1 -mr-1 flex opacity-100 transition-opacity [@media(hover:hover)]:opacity-0 [@media(hover:hover)]:group-focus-within:opacity-100 [@media(hover:hover)]:group-hover:opacity-100">
              <Button
                variant="ghost"
                size="icon"
                aria-label={`Edit ${task.title}`}
                onClick={() => setIsEditing(true)}
              >
                <PencilIcon />
              </Button>
              <Button
                variant="danger-ghost"
                size="icon"
                aria-label={`Delete ${task.title}`}
                onClick={onDelete}
              >
                <TrashIcon />
              </Button>
            </div>
          </div>
          {task.description && (
            <p className="mt-1 line-clamp-3 text-sm break-words whitespace-pre-line text-muted">
              {task.description}
            </p>
          )}
          <div className="mt-3 flex flex-wrap items-center justify-between gap-2">
            <TaskStatusSelect
              label={`Status of ${task.title}`}
              value={task.status}
              onChange={changeStatus}
              disabled={isSavingStatus}
            />
            <time dateTime={task.createdAt} className="font-mono text-[11px] text-muted">
              Created {formatDateTime(task.createdAt)}
            </time>
          </div>
        </>
      )}
    </li>
  )
}
