import React from 'react'

/**
 * Card — flat white card component.
 *
 * Props:
 *   title    : string — renders card-header with title
 *   subtitle : string
 *   actions  : ReactNode — right side of header
 *   hoverable: boolean
 *   padding  : 'sm' | 'md' | 'lg'
 */
export default function Card({
  children,
  title,
  subtitle,
  actions,
  hoverable = false,
  padding = 'md',
  className = '',
  ...rest
}) {
  const paddingClass = padding === 'sm' ? 'card-sm' : padding === 'lg' ? 'card-lg' : ''
  const classes = [
    'card-component',
    hoverable ? 'hoverable' : '',
    paddingClass,
    className,
  ].filter(Boolean).join(' ')

  return (
    <div className={classes} {...rest}>
      {(title || actions) && (
        <div className="card-header">
          <div>
            {title && <div className="card-title">{title}</div>}
            {subtitle && <div className="card-subtitle">{subtitle}</div>}
          </div>
          {actions && <div>{actions}</div>}
        </div>
      )}
      {children}
    </div>
  )
}
