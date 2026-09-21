import React from 'react'

/**
 * Button — primary reusable button component.
 * All styling comes from components.css (.btn, .btn-primary, etc.)
 *
 * Props:
 *   variant  : 'primary' | 'secondary' | 'ghost' | 'danger'  (default: 'primary')
 *   size     : 'sm' | 'md' | 'lg'                            (default: 'md')
 *   fullWidth: boolean
 *   loading  : boolean — shows spinner and disables click
 *   leftIcon : ReactNode
 *   rightIcon: ReactNode
 *   ...rest  : passed to <button>
 */
export default function Button({
  children,
  variant = 'primary',
  size = 'md',
  fullWidth = false,
  loading = false,
  isLoading,
  block,
  leftIcon,
  rightIcon,
  className = '',
  disabled,
  ...rest
}) {
  const isActuallyLoading = Boolean(loading || isLoading)
  const isFullWidth = Boolean(fullWidth || block)
  const sizeClass = size === 'sm' ? 'btn-sm' : size === 'lg' ? 'btn-lg' : ''
  const classes = [
    'btn',
    `btn-${variant}`,
    sizeClass,
    isFullWidth ? 'btn-full' : '',
    className,
  ].filter(Boolean).join(' ')

  return (
    <button className={classes} disabled={disabled || isActuallyLoading} {...rest}>
      {isActuallyLoading && <span className="btn-spinner" aria-hidden="true" />}
      {!isActuallyLoading && leftIcon && <span className="btn-icon">{leftIcon}</span>}
      {children}
      {!isActuallyLoading && rightIcon && <span className="btn-icon">{rightIcon}</span>}
    </button>
  )
}
