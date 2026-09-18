import { useRef, useState } from 'react'

import { Button } from '../../shared/Button'
import { toMessage } from '../../shared/apiClient'
import type { TaskDraft } from './types'

const MAX_TITLE_LENGTH = 255

const FIELD_CLASSES =
  'w-full rounded-lg border border-line bg-panel px-3 py-2 text-sm placeholder:text-muted/70 focus:border-progress focus:outline-none'

interface TaskFormProps {
  initial?: TaskDraft
  submitLabel: string
  onSubmit: (draft: TaskDraft) => Promise<unknown>
  onCancel?: () => void
}

export function TaskForm({ initial, submitLabel, onSubmit, onCancel }: TaskFormProps) {
  const [title, setTitle] = useState(initial?.title ?? '')
  const [description, setDescription] = useState(initial?.description ?? '')
  const [error, setError] = useState<string | null>(null)
  const [isSaving, setIsSaving] = useState(false)
  const titleRef = useRef<HTMLInputElement>(null)

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    if (!title.trim()) {
      setError('Title must not be empty')
      return
    }

    setIsSaving(true)
    try {
      await onSubmit({ title, description })
      if (!initial) {
        setTitle('')
        setDescription('')
        titleRef.current?.focus()
      }
      setError(null)
    } catch (caught: unknown) {
      setError(toMessage(caught))
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      onKeyDown={(event) => {
        if (event.key === 'Escape' && onCancel) onCancel()
      }}
      className="space-y-2"
    >
      <input
        ref={titleRef}
        value={title}
        onChange={(event) => setTitle(event.target.value)}
        placeholder="Task title"
        required
        autoFocus
        maxLength={MAX_TITLE_LENGTH}
        aria-label="Task title"
        className={FIELD_CLASSES}
      />
      <textarea
        value={description}
        onChange={(event) => setDescription(event.target.value)}
        placeholder="Description (optional)"
        rows={2}
        aria-label="Task description"
        className={`${FIELD_CLASSES} resize-y`}
      />
      {error && (
        <p className="text-xs font-medium text-danger" role="alert">
          {error}
        </p>
      )}
      <div className="flex gap-2">
        <Button type="submit" variant="primary" size="sm" disabled={isSaving}>
          {isSaving ? 'Saving...' : submitLabel}
        </Button>
        {onCancel && (
          <Button variant="ghost" size="sm" onClick={onCancel}>
            Cancel
          </Button>
        )}
      </div>
    </form>
  )
}
