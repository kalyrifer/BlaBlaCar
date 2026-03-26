import { HTMLAttributes } from 'react'
import { clsx } from 'clsx'
import styles from './Card.module.css'

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'elevated' | 'outlined'
  padding?: 'none' | 'sm' | 'md' | 'lg'
}

export function Card({
  className,
  variant = 'default',
  padding = 'md',
  children,
  ...props
}: CardProps) {
  return (
    <div
      className={clsx(
        styles.card,
        styles[variant],
        styles[`padding-${padding}`],
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
}

export function CardHeader({
  className,
  children,
  ...props
}: HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={clsx(styles.header, className)} {...props}>
      {children}
    </div>
  )
}

export function CardContent({
  className,
  children,
  ...props
}: HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={clsx(styles.content, className)} {...props}>
      {children}
    </div>
  )
}

export function CardFooter({
  className,
  children,
  ...props
}: HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={clsx(styles.footer, className)} {...props}>
      {children}
    </div>
  )
}
