import { useCallback, useEffect, useState } from 'react'

import { toMessage } from '../../shared/apiClient'
import { tasksApi } from './api'
import type { Task, TaskStatus } from './types'

interface TaskChanges {
  title?: string
  description?: string | null
  status?: TaskStatus
}

export function useTasks(boardId: number | null) {
  const [loaded, setLoaded] = useState<{ boardId: number; tasks: Task[] } | null>(null)
  const [failure, setFailure] = useState<{ boardId: number; message: string } | null>(null)
  const [reloadToken, setReloadToken] = useState(0)

  useEffect(() => {
    if (boardId === null) return

    const controller = new AbortController()

    tasksApi
      .listByBoard(boardId, controller.signal)
      .then((tasks) => {
        setLoaded({ boardId, tasks })
        setFailure(null)
      })
      .catch((caught: unknown) => {
        if (controller.signal.aborted) return
        setFailure({ boardId, message: toMessage(caught) })
      })

    return () => controller.abort()
  }, [boardId, reloadToken])

  const error = failure?.boardId === boardId ? failure.message : null
  const tasks = loaded?.boardId === boardId ? loaded.tasks : []
  const isLoading = boardId !== null && loaded?.boardId !== boardId && error === null

  const reload = useCallback(() => {
    setFailure(null)
    setReloadToken((token) => token + 1)
  }, [])

  const createTask = useCallback(
    async (title: string, description: string): Promise<Task> => {
      if (boardId === null) throw new Error('Select a board first')
      const task = await tasksApi.create(boardId, title, description || null)
      reload()
      return task
    },
    [boardId, reload],
  )

  const updateTask = useCallback(
    async (taskId: number, changes: TaskChanges): Promise<Task> => {
      const task = await tasksApi.update(taskId, changes)
      setLoaded((current) =>
        current === null
          ? current
          : { ...current, tasks: current.tasks.map((item) => (item.id === task.id ? task : item)) },
      )
      reload()
      return task
    },
    [reload],
  )

  const deleteTask = useCallback(
    async (taskId: number): Promise<void> => {
      await tasksApi.remove(taskId)
      setLoaded((current) =>
        current === null
          ? current
          : { ...current, tasks: current.tasks.filter((item) => item.id !== taskId) },
      )
      reload()
    },
    [reload],
  )

  return { tasks, isLoading, error, reload, createTask, updateTask, deleteTask }
}
