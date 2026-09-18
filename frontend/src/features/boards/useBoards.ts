import { useCallback, useEffect, useState } from 'react'

import { toMessage } from '../../shared/apiClient'
import { boardsApi } from './api'
import type { Board } from './types'

export function useBoards() {
  const [loaded, setLoaded] = useState<Board[] | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [reloadToken, setReloadToken] = useState(0)

  useEffect(() => {
    const controller = new AbortController()

    boardsApi
      .list(controller.signal)
      .then((boards) => {
        setLoaded(boards)
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

  const createBoard = useCallback(
    async (name: string): Promise<Board> => {
      const board = await boardsApi.create(name)
      setLoaded((current) => [board, ...(current ?? [])])
      reload()
      return board
    },
    [reload],
  )

  const renameBoard = useCallback(
    async (boardId: number, name: string): Promise<Board> => {
      const board = await boardsApi.rename(boardId, name)
      setLoaded((current) => (current ?? []).map((item) => (item.id === board.id ? board : item)))
      reload()
      return board
    },
    [reload],
  )

  const deleteBoard = useCallback(
    async (boardId: number): Promise<void> => {
      await boardsApi.remove(boardId)
      setLoaded((current) => (current ?? []).filter((item) => item.id !== boardId))
      reload()
    },
    [reload],
  )

  return {
    boards: loaded ?? [],
    isLoading: loaded === null && error === null,
    error,
    reload,
    createBoard,
    renameBoard,
    deleteBoard,
  }
}
