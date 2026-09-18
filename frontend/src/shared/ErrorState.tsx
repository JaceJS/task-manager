import { Button } from './Button'
import { AlertIcon } from './icons'

interface ErrorStateProps {
  message: string
  onRetry?: () => void
}

export function ErrorState({ message, onRetry }: ErrorStateProps) {
  return (
    <div
      className="flex items-start gap-3 rounded-xl border border-danger/30 bg-danger/5 px-4 py-3 text-sm"
      role="alert"
    >
      <AlertIcon className="mt-0.5 shrink-0 text-danger" />
      <div className="min-w-0 flex-1 space-y-2">
        <p className="text-ink">{message}</p>
        {onRetry && (
          <Button size="sm" onClick={onRetry}>
            Try again
          </Button>
        )}
      </div>
    </div>
  )
}
