import { useState } from 'react'

import { Button } from '../../shared/Button'
import { PlusIcon } from '../../shared/icons'
import { toMessage } from '../../shared/apiClient'

const MAX_NAME_LENGTH = 255

interface BoardFormProps {
  initialName?: string
  submitLabel: string
  savingLabel: string
  onSubmit: (name: string) => Promise<unknown>
  onCancel: () => void
  large?: boolean
}

export function BoardForm({
  initialName = '',
  submitLabel,
  savingLabel,
  onSubmit,
  onCancel,
  large = false,
}: BoardFormProps) {
  const [name, setName] = useState(initialName)
  const [error, setError] = useState<string | null>(null)
  const [isSaving, setIsSaving] = useState(false)

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    if (!name.trim()) {
      setError('Name must not be empty')
      return
    }

    setIsSaving(true)
    try {
      await onSubmit(name)
    } catch (caught: unknown) {
      setError(toMessage(caught))
      setIsSaving(false)
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      onKeyDown={(event) => {
        if (event.key === 'Escape') onCancel()
      }}
      className="space-y-2"
    >
      <input
        value={name}
        onChange={(event) => setName(event.target.value)}
        placeholder="Board name"
        required
        autoFocus
        maxLength={MAX_NAME_LENGTH}
        aria-label="Board name"
        className={`w-full rounded-lg border border-line bg-panel px-3 placeholder:text-muted/70 focus:border-progress focus:outline-none ${
          large ? 'py-1.5 text-xl font-bold' : 'py-2 text-sm'
        }`}
      />
      {error && (
        <p className="text-xs font-medium text-danger" role="alert">
          {error}
        </p>
      )}
      <div className="flex gap-2">
        <Button type="submit" variant="primary" size="sm" disabled={isSaving}>
          {isSaving ? savingLabel : submitLabel}
        </Button>
        <Button variant="ghost" size="sm" onClick={onCancel}>
          Cancel
        </Button>
      </div>
    </form>
  )
}

export function NewBoardForm({ onCreate }: { onCreate: (name: string) => Promise<unknown> }) {
  const [isOpen, setIsOpen] = useState(false)

  if (!isOpen) {
    return (
      <Button variant="ghost" size="sm" className="w-full" onClick={() => setIsOpen(true)}>
        <PlusIcon />
        New board
      </Button>
    )
  }

  return (
    <BoardForm
      submitLabel="Create board"
      savingLabel="Creating..."
      onCancel={() => setIsOpen(false)}
      onSubmit={async (name) => {
        await onCreate(name)
        setIsOpen(false)
      }}
    />
  )
}
