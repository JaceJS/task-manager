import type { Board } from '../boards/types'
import type { Task } from '../tasks/types'

export interface BoardInTrash extends Board {
  deletedAt: string
}

export interface TaskInTrash extends Task {
  boardName: string
  deletedAt: string
}
