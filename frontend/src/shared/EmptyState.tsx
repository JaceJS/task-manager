interface EmptyStateProps {
  message: string
  compact?: boolean
}

export function EmptyState({ message, compact = false }: EmptyStateProps) {
  return (
    <p
      className={`rounded-xl border border-dashed border-line text-center text-sm text-muted ${
        compact ? 'px-3 py-5' : 'px-6 py-10'
      }`}
    >
      {message}
    </p>
  )
}
