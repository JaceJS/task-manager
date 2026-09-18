import type { Board } from './types'

interface BoardListProps {
  boards: Board[]
  selectedBoardId: number | null
  onSelect: (boardId: number) => void
}

export function BoardList({ boards, selectedBoardId, onSelect }: BoardListProps) {
  return (
    <ul className="space-y-0.5">
      {boards.map((board) => {
        const isSelected = board.id === selectedBoardId
        return (
          <li key={board.id}>
            <button
              type="button"
              onClick={() => onSelect(board.id)}
              aria-current={isSelected}
              className={`flex w-full items-center gap-2.5 rounded-lg px-2 py-1.5 text-left text-sm transition-colors ${
                isSelected
                  ? 'bg-surface font-semibold text-ink'
                  : 'text-muted hover:bg-surface/70 hover:text-ink'
              }`}
            >
              <span
                aria-hidden="true"
                className={`grid size-6 shrink-0 place-items-center rounded-md text-xs font-bold uppercase ${
                  isSelected ? 'bg-ink text-white' : 'bg-line/70 text-muted'
                }`}
              >
                {board.name.charAt(0)}
              </span>
              <span className="truncate">{board.name}</span>
            </button>
          </li>
        )
      })}
    </ul>
  )
}
