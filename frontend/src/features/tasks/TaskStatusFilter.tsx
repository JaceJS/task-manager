import {
  STATUS_LABELS,
  STATUS_STYLE,
  TASK_STATUSES,
  type StatusCounts,
  type TaskStatus,
} from './types'

export function StatusBar({ counts }: { counts: StatusCounts }) {
  const total = TASK_STATUSES.reduce((sum, status) => sum + counts[status], 0)
  const summary = TASK_STATUSES.map(
    (status) => `${counts[status]} ${STATUS_LABELS[status].toLowerCase()}`,
  ).join(', ')

  return (
    <div className="flex items-center gap-3">
      <div
        role="img"
        aria-label={summary}
        className="flex h-2 flex-1 overflow-hidden rounded-full bg-line"
      >
        {total > 0 &&
          TASK_STATUSES.map((status) => (
            <div
              key={status}
              className={`transition-[width] duration-300 ${STATUS_STYLE[status].dot}`}
              style={{ width: `${(counts[status] / total) * 100}%` }}
            />
          ))}
      </div>
      <span className="shrink-0 text-xs font-medium text-muted">
        {total === 0 ? 'No tasks yet' : `${counts.DONE} of ${total} done`}
      </span>
    </div>
  )
}

interface TaskStatusFilterProps {
  counts: StatusCounts
  value: TaskStatus | null
  onChange: (status: TaskStatus | null) => void
}

export function TaskStatusFilter({ counts, value, onChange }: TaskStatusFilterProps) {
  const total = TASK_STATUSES.reduce((sum, status) => sum + counts[status], 0)
  const chip = 'inline-flex h-8 items-center gap-2 rounded-full border px-3 text-sm font-medium transition-colors'
  const idle = 'border-line bg-panel text-muted hover:text-ink'

  return (
    <div role="group" aria-label="Filter tasks by status" className="flex flex-wrap gap-2">
      <button
        type="button"
        aria-pressed={value === null}
        onClick={() => onChange(null)}
        className={`${chip} ${value === null ? 'border-ink bg-ink text-white' : idle}`}
      >
        All <Count value={total} />
      </button>
      {TASK_STATUSES.map((status) => {
        const style = STATUS_STYLE[status]
        const isActive = value === status
        return (
          <button
            key={status}
            type="button"
            aria-pressed={isActive}
            onClick={() => onChange(isActive ? null : status)}
            className={`${chip} ${isActive ? style.pill : idle}`}
          >
            <span className={`size-2 rounded-full ${style.dot}`} />
            {STATUS_LABELS[status]} <Count value={counts[status]} />
          </button>
        )
      })}
    </div>
  )
}

function Count({ value }: { value: number }) {
  return <span className="font-mono text-xs opacity-70">{value}</span>
}
