import { clsx } from 'clsx'
import { ButtonHTMLAttributes, forwardRef } from 'react'
import styles from './Button.module.css'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  loading?: boolean
  fullWidth?: boolean
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ 
    className, 
    variant = 'primary', 
    size = 'md', 
    loading = false, 
    fullWidth = false,
    disabled,
    children,
    ...props 
  }, ref) => {
    return (
      <button
        ref={ref}
        className={clsx(
          styles.button,
          styles[variant],
          styles[size],
          fullWidth && styles.fullWidth,
          loading && styles.loading,
          className
        )}
        disabled={disabled || loading}
        {...props}
      >
        {loading && <span className={styles.spinner} />}
        <span className={loading ? styles.hiddenText : undefined}>{children}</span>
      </button>
    )
  }
)

Button.displayName = 'Button'
