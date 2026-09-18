import { apiClient } from '../../shared/apiClient'
import type { Board } from '../boards/types'
import type { Task } from '../tasks/types'
import type { BoardInTrash, TaskInTrash } from './types'

export const trashApi = {
  listBoards: (signal?: AbortSignal) => apiClient.get<BoardInTrash[]>('/api/trash/boards', signal),
  listTasks: (signal?: AbortSignal) => apiClient.get<TaskInTrash[]>('/api/trash/tasks', signal),
  restoreBoard: (boardId: number) => apiClient.post<Board>(`/api/boards/${boardId}/restore`),
  restoreTask: (taskId: number) => apiClient.post<Task>(`/api/tasks/${taskId}/restore`),
  deleteBoard: (boardId: number) => apiClient.delete(`/api/trash/boards/${boardId}`),
  deleteTask: (taskId: number) => apiClient.delete(`/api/trash/tasks/${taskId}`),
}
