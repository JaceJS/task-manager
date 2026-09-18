interface LoadingStateProps {
  label?: string
  rows?: number
}

export function LoadingState({ label = 'Loading...', rows = 3 }: LoadingStateProps) {
  return (
    <div role="status" className="space-y-2">
      <span className="sr-only">{label}</span>
      {Array.from({ length: rows }, (_, index) => (
        <div key={index} className="h-14 animate-pulse rounded-xl bg-line/60" />
      ))}
    </div>
  )
}
