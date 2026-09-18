import { apiClient } from '../../shared/apiClient'
import type { Board } from './types'

export const boardsApi = {
  list: (signal?: AbortSignal) => apiClient.get<Board[]>('/api/boards', signal),
  create: (name: string) => apiClient.post<Board>('/api/boards', { name }),
  rename: (boardId: number, name: string) =>
    apiClient.patch<Board>(`/api/boards/${boardId}`, { name }),
  remove: (boardId: number) => apiClient.delete(`/api/boards/${boardId}`),
}
