import React, { useState, useId } from 'react'

/**
 * FormInput — labelled input/select/textarea with inline validation.
 *
 * Props:
 *   label      : string
 *   type       : input type  (default: 'text')
 *   error      : string — validation error message
 *   hint       : string — helper text below input
 *   required   : boolean
 *   leftIcon   : ReactNode
 *   rightIcon  : ReactNode
 *   as         : 'input' | 'select' | 'textarea'  (default: 'input')
 */
export default function FormInput({
  label,
  type = 'text',
  error,
  hint,
  required = false,
  leftIcon,
  rightIcon,
  as: Component = 'input',
  className = '',
  id: externalId,
  children,  // for <select> options
  ...rest
}) {
  const autoId = useId()
  const id = externalId || autoId

  const wrapperClasses = [
    'form-input-wrapper',
    leftIcon  ? 'has-left'  : '',
    rightIcon ? 'has-right' : '',
  ].filter(Boolean).join(' ')

  const inputClasses = [
    Component === 'select' ? 'form-control form-select' : 'form-control',
    error ? 'error' : '',
    className,
  ].filter(Boolean).join(' ')

  return (
    <div className="form-group">
      {label && (
        <label className="form-label" htmlFor={id}>
          {label}
          {required && <span className="required" aria-hidden="true">*</span>}
        </label>
      )}
      <div className={wrapperClasses}>
        {leftIcon && <span className="form-icon-left" aria-hidden="true">{leftIcon}</span>}
        {Component === 'input' ? (
          <input
            id={id}
            type={type}
            className={inputClasses}
            aria-invalid={!!error}
            aria-describedby={error ? `${id}-error` : hint ? `${id}-hint` : undefined}
            {...rest}
          />
        ) : (
          <Component
            id={id}
            className={inputClasses}
            aria-invalid={!!error}
            aria-describedby={error ? `${id}-error` : hint ? `${id}-hint` : undefined}
            {...rest}
          >
            {children}
          </Component>
        )}
        {rightIcon && <span className="form-icon-right" aria-hidden="true">{rightIcon}</span>}
      </div>
      {error && <span id={`${id}-error`} className="form-error" role="alert">{error}</span>}
      {!error && hint && <span id={`${id}-hint`} className="form-hint">{hint}</span>}
    </div>
  )
}

/* ─── Password Strength Meter (used on Register page) ──────────────────────── */
export function PasswordStrengthMeter({ password }) {
  const score = calcScore(password)
  const labels = ['', 'Weak', 'Fair', 'Good', 'Strong']
  const barClasses = ['', 'weak', 'fair', 'strong', 'strong']

  return (
    <div aria-label={`Password strength: ${labels[score]}`}>
      <div className="strength-meter">
        {[1, 2, 3, 4].map(i => (
          <div
            key={i}
            className={`strength-bar ${i <= score ? barClasses[score] : ''}`}
          />
        ))}
      </div>
      {password && (
        <div className="strength-label">{labels[score] || 'Very weak'}</div>
      )}
    </div>
  )
}

function calcScore(pw = '') {
  if (!pw) return 0
  let s = 0
  if (pw.length >= 8)  s++
  if (/[A-Z]/.test(pw)) s++
  if (/[0-9]/.test(pw)) s++
  if (/[^A-Za-z0-9]/.test(pw)) s++
  return s
}
