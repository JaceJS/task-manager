import { useCallback, useState } from 'react'

import { toMessage } from './apiClient'

export function useActionError() {
  const [error, setError] = useState<string | null>(null)

  const run = useCallback(async (action: () => Promise<unknown>, onSuccess?: () => void) => {
    try {
      setError(null)
      await action()
      onSuccess?.()
    } catch (caught: unknown) {
      setError(toMessage(caught))
    }
  }, [])

  const clear = useCallback(() => setError(null), [])

  return { error, run, clear }
}
