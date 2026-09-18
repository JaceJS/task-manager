import { useState, type ReactNode } from 'react'

import { Button } from '../../shared/Button'
import type { ConfirmRequest } from '../../shared/ConfirmDialog'
import { EmptyState } from '../../shared/EmptyState'
import { ErrorState } from '../../shared/ErrorState'
import { LoadingState } from '../../shared/LoadingState'
import { formatDateTime } from '../../shared/formatDateTime'
import { useActionError } from '../../shared/useActionError'
import { STATUS_LABELS, STATUS_STYLE } from '../tasks/types'
import { useTrash } from './useTrash'

interface TrashPageProps {
  onConfirm: (request: ConfirmRequest) => void
  onBoardRestored: () => void
  onTaskRestored: () => void
}

export function TrashPage({ onConfirm, onBoardRestored, onTaskRestored }: TrashPageProps) {
  const trash = useTrash()
  const action = useActionError()

  const askDeleteForever = (kind: 'board' | 'task', name: string, remove: () => Promise<unknown>) =>
    onConfirm({
      title: `Delete '${name}' permanently?`,
      body: `This ${kind} will be gone for good. This cannot be undone.`,
      confirmLabel: 'Delete permanently',
      onConfirm: () => action.run(remove),
    })

  const isEmpty = trash.boards.length === 0 && trash.tasks.length === 0

  return (
    <div className="space-y-6">
      <header className="space-y-1">
        <h1 className="text-2xl font-bold tracking-tight">Trash</h1>
        <p className="text-sm text-muted">
          Deleted boards and tasks stay here until you restore them or delete them permanently.
        </p>
      </header>

      {action.error && <ErrorState message={action.error} />}
      {trash.isLoading && <LoadingState label="Loading trash..." />}
      {trash.error && <ErrorState message={trash.error} onRetry={trash.reload} />}

      {!trash.isLoading && !trash.error && isEmpty && <EmptyState message="Trash is empty." />}

      {!trash.isLoading && !trash.error && !isEmpty && (
        <>
          <TrashSection title="Boards" count={trash.boards.length} empty="No boards in trash.">
            {trash.boards.map((board) => (
              <TrashRow
                key={board.id}
                title={board.name}
                details={`Deleted ${formatDateTime(board.deletedAt)}`}
                onRestore={() => action.run(() => trash.restoreBoard(board.id), onBoardRestored)}
                onDelete={() =>
                  askDeleteForever('board', board.name, () =>
                    trash.deleteBoardPermanently(board.id),
                  )
                }
              />
            ))}
          </TrashSection>

          <TrashSection title="Tasks" count={trash.tasks.length} empty="No tasks in trash.">
            {trash.tasks.map((task) => (
              <TrashRow
                key={task.id}
                title={task.title}
                details={`From ${task.boardName} · Deleted ${formatDateTime(task.deletedAt)}`}
                badge={
                  <span className="inline-flex items-center gap-1.5 text-xs font-medium text-muted">
                    <span className={`size-2 rounded-full ${STATUS_STYLE[task.status].dot}`} />
                    {STATUS_LABELS[task.status]}
                  </span>
                }
                onRestore={() => action.run(() => trash.restoreTask(task.id), onTaskRestored)}
                onDelete={() =>
                  askDeleteForever('task', task.title, () => trash.deleteTaskPermanently(task.id))
                }
              />
            ))}
          </TrashSection>
        </>
      )}
    </div>
  )
}

interface TrashSectionProps {
  title: string
  count: number
  empty: string
  children: ReactNode
}

function TrashSection({ title, count, empty, children }: TrashSectionProps) {
  return (
    <section aria-label={title} className="space-y-2">
      <h2 className="flex items-center gap-2 text-xs font-bold tracking-wider text-muted uppercase">
        {title}
        <span className="rounded-full bg-panel px-2 font-mono text-xs">{count}</span>
      </h2>
      {count === 0 ? <EmptyState compact message={empty} /> : <ul className="space-y-2">{children}</ul>}
    </section>
  )
}

interface TrashRowProps {
  title: string
  details: string
  badge?: ReactNode
  onRestore: () => Promise<unknown>
  onDelete: () => void
}

function TrashRow({ title, details, badge, onRestore, onDelete }: TrashRowProps) {
  const [isRestoring, setIsRestoring] = useState(false)

  const restore = async () => {
    setIsRestoring(true)
    try {
      await onRestore()
    } finally {
      setIsRestoring(false)
    }
  }

  return (
    <li className="flex flex-wrap items-center gap-3 rounded-xl border border-line bg-panel p-3 shadow-sm">
      <div className="min-w-0 flex-1">
        <p className="text-sm font-semibold break-words">{title}</p>
        <div className="mt-0.5 flex flex-wrap items-center gap-x-3 gap-y-1">
          {badge}
          <span className="font-mono text-[11px] text-muted">{details}</span>
        </div>
      </div>
      <div className="flex gap-1">
        <Button
          size="sm"
          onClick={restore}
          disabled={isRestoring}
          aria-label={`Restore ${title}`}
        >
          {isRestoring ? 'Restoring...' : 'Restore'}
        </Button>
        <Button
          variant="danger-ghost"
          size="sm"
          onClick={onDelete}
          disabled={isRestoring}
          aria-label={`Delete ${title} permanently`}
        >
          Delete permanently
        </Button>
      </div>
    </li>
  )
}
