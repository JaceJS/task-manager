import { apiClient } from '../../shared/apiClient'
import type { Task, TaskStatus } from './types'

interface TaskChanges {
  title?: string
  description?: string | null
  status?: TaskStatus
}

export const tasksApi = {
  listByBoard: (boardId: number, signal?: AbortSignal) =>
    apiClient.get<Task[]>(`/api/boards/${boardId}/tasks`, signal),
  create: (boardId: number, title: string, description: string | null) =>
    apiClient.post<Task>(`/api/boards/${boardId}/tasks`, { title, description }),
  update: (taskId: number, changes: TaskChanges) =>
    apiClient.patch<Task>(`/api/tasks/${taskId}`, changes),
  remove: (taskId: number) => apiClient.delete(`/api/tasks/${taskId}`),
}
