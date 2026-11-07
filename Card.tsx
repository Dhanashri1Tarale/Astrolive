import type { ReactNode } from 'react'

export default function Card({
  children,
  className = '',
}: {
  children: ReactNode
  className?: string
}) {
  return (
    <div
      className={`rounded-2xl border border-white/5 bg-surface/80 p-6 shadow-glow backdrop-blur-sm ${className}`}
    >
      {children}
    </div>
  )
}
