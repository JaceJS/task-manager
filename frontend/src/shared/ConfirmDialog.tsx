import { useEffect, useRef } from 'react'

import { Button } from './Button'

export interface ConfirmRequest {
  title: string
  body: string
  confirmLabel: string
  onConfirm: () => void
}

interface ConfirmDialogProps {
  request: ConfirmRequest | null
  onClose: () => void
}

export function ConfirmDialog({ request, onClose }: ConfirmDialogProps) {
  const dialogRef = useRef<HTMLDialogElement>(null)

  useEffect(() => {
    const dialog = dialogRef.current
    if (!dialog) return
    if (request && !dialog.open) dialog.showModal()
    if (!request && dialog.open) dialog.close()
  }, [request])

  if (!request) return null

  const confirm = () => {
    request.onConfirm()
    onClose()
  }

  return (
    <dialog
      ref={dialogRef}
      onClose={onClose}
      className="m-auto w-[min(26rem,calc(100vw-2rem))] rounded-2xl bg-panel p-6 text-ink shadow-xl"
    >
      <h2 className="text-lg font-semibold">{request.title}</h2>
      <p className="mt-2 text-sm text-muted">{request.body}</p>
      <div className="mt-6 flex justify-end gap-2">
        <Button variant="ghost" onClick={onClose}>
          Cancel
        </Button>
        <Button variant="danger" onClick={confirm}>
          {request.confirmLabel}
        </Button>
      </div>
    </dialog>
  )
}
