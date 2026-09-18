import { useState, type ReactNode } from 'react'

import { Button } from '../../shared/Button'
import { PencilIcon, TrashIcon } from '../../shared/icons'
import { BoardForm } from './BoardForm'
import type { Board } from './types'

interface BoardHeaderProps {
  board: Board
  onRename: (name: string) => Promise<unknown>
  onDelete: () => void
  children?: ReactNode
}

export function BoardHeader({ board, onRename, onDelete, children }: BoardHeaderProps) {
  const [isRenaming, setIsRenaming] = useState(false)

  return (
    <header className="space-y-3">
      {isRenaming ? (
        <div className="max-w-xl">
          <BoardForm
            large
            initialName={board.name}
            submitLabel="Save"
            savingLabel="Saving..."
            onCancel={() => setIsRenaming(false)}
            onSubmit={async (name) => {
              await onRename(name)
              setIsRenaming(false)
            }}
          />
        </div>
      ) : (
        <div className="flex items-start justify-between gap-4">
          <h1 className="min-w-0 text-2xl font-bold tracking-tight break-words">{board.name}</h1>
          <div className="flex shrink-0 gap-1">
            <Button variant="ghost" size="sm" onClick={() => setIsRenaming(true)}>
              <PencilIcon />
              Rename
            </Button>
            <Button variant="danger-ghost" size="sm" onClick={onDelete}>
              <TrashIcon />
              Delete board
            </Button>
          </div>
        </div>
      )}
      {children}
    </header>
  )
}
