import { HTMLAttributes } from 'react'
import { clsx } from 'clsx'
import styles from './Skeleton.module.css'

interface SkeletonProps extends HTMLAttributes<HTMLDivElement> {
  width?: string | number
  height?: string | number
  variant?: 'text' | 'rectangular' | 'circular'
  animation?: 'pulse' | 'wave' | 'none'
}

export function Skeleton({
  className,
  width,
  height,
  variant = 'rectangular',
  animation = 'pulse',
  style,
  ...props
}: SkeletonProps) {
  return (
    <div
      className={clsx(
        styles.skeleton,
        styles[variant],
        styles[animation],
        className
      )}
      style={{
        width,
        height,
        ...style
      }}
      {...props}
    />
  )
}
