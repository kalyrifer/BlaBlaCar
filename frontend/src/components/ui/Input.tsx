import { InputHTMLAttributes, forwardRef } from 'react'
import { clsx } from 'clsx'
import styles from './Input.module.css'

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  helperText?: string
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, label, error, helperText, id, ...props }, ref) => {
    const inputId = id || label?.toLowerCase().replace(/\s+/g, '-')
    
    return (
      <div className={styles.wrapper}>
        {label && (
          <label htmlFor={inputId} className={styles.label}>
            {label}
          </label>
        )}
        <input
          ref={ref}
          id={inputId}
          className={clsx(
            styles.input,
            error && styles.error,
            className
          )}
          {...props}
        />
        {error && <span className={styles.errorText}>{error}</span>}
        {helperText && !error && (
          <span className={styles.helperText}>{helperText}</span>
        )}
      </div>
    )
  }
)

Input.displayName = 'Input'
