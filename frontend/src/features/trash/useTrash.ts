import { useCallback, useEffect, useState } from 'react'

import { toMessage } from '../../shared/apiClient'
import { trashApi } from './api'
import type { BoardInTrash, TaskInTrash } from './types'

interface TrashContents {
  boards: BoardInTrash[]
  tasks: TaskInTrash[]
}

export function useTrash() {
  const [contents, setContents] = useState<TrashContents | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [reloadToken, setReloadToken] = useState(0)

  useEffect(() => {
    const controller = new AbortController()

    Promise.all([
      trashApi.listBoards(controller.signal),
      trashApi.listTasks(controller.signal),
    ])
      .then(([boards, tasks]) => {
        setContents({ boards, tasks })
        setError(null)
      })
      .catch((caught: unknown) => {
        if (controller.signal.aborted) return
        setError(toMessage(caught))
      })

    return () => controller.abort()
  }, [reloadToken])

  const reload = useCallback(() => {
    setError(null)
    setReloadToken((token) => token + 1)
  }, [])

  const afterAction = useCallback(
    async (action: () => Promise<unknown>, remove: (current: TrashContents) => TrashContents) => {
      await action()
      setContents((current) => (current === null ? current : remove(current)))
      reload()
    },
    [reload],
  )

  const withoutBoard = (boardId: number) => (current: TrashContents) => ({
    ...current,
    boards: current.boards.filter((board) => board.id !== boardId),
  })
  const withoutTask = (taskId: number) => (current: TrashContents) => ({
    ...current,
    tasks: current.tasks.filter((task) => task.id !== taskId),
  })

  return {
    boards: contents?.boards ?? [],
    tasks: contents?.tasks ?? [],
    isLoading: contents === null && error === null,
    error,
    reload,
    restoreBoard: (boardId: number) =>
      afterAction(() => trashApi.restoreBoard(boardId), withoutBoard(boardId)),
    restoreTask: (taskId: number) =>
      afterAction(() => trashApi.restoreTask(taskId), withoutTask(taskId)),
    deleteBoardPermanently: (boardId: number) =>
      afterAction(() => trashApi.deleteBoard(boardId), withoutBoard(boardId)),
    deleteTaskPermanently: (taskId: number) =>
      afterAction(() => trashApi.deleteTask(taskId), withoutTask(taskId)),
  }
}
