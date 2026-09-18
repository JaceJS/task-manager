import { STATUS_LABELS, STATUS_STYLE, TASK_STATUSES, type TaskStatus } from './types'

interface TaskStatusSelectProps {
  value: TaskStatus
  onChange: (status: TaskStatus) => void
  label: string
  disabled?: boolean
}

export function TaskStatusSelect({ value, onChange, label, disabled = false }: TaskStatusSelectProps) {
  const style = STATUS_STYLE[value]

  return (
    <div
      className={`relative inline-flex h-7 items-center rounded-full border ${style.pill} ${
        disabled ? 'opacity-50' : ''
      }`}
    >
      <span className={`pointer-events-none absolute left-2.5 size-2 rounded-full ${style.dot}`} />
      <select
        aria-label={label}
        value={value}
        disabled={disabled}
        onChange={(event) => onChange(event.target.value as TaskStatus)}
        className="h-full cursor-pointer appearance-none rounded-full bg-transparent pr-7 pl-6 text-xs font-semibold"
      >
        {TASK_STATUSES.map((status) => (
          <option key={status} value={status}>
            {STATUS_LABELS[status]}
          </option>
        ))}
      </select>
      <svg
        viewBox="0 0 12 12"
        width="10"
        height="10"
        aria-hidden="true"
        className="pointer-events-none absolute right-2.5"
      >
        <path d="M2 4l4 4 4-4" fill="none" stroke="currentColor" strokeWidth="1.8" />
      </svg>
    </div>
  )
}
