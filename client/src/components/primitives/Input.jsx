import React, { forwardRef, useId } from 'react';

/**
 * Input Primitive
 * States: default, hover, focus-visible (2px accent ring), disabled, error
 */
export const Input = forwardRef(function Input(
  {
    label,
    error,
    helperText,
    id,
    disabled = false,
    className = '',
    required = false,
    ...props
  },
  ref
) {
  const generatedId = useId();
  const inputId = id || generatedId;
  const helperId = `${inputId}-helper`;

  return (
    <div className={`nexus-field-container ${error ? 'nexus-field--error' : ''}`}>
      {label && (
        <div className="nexus-field-header">
          <label htmlFor={inputId} className="nexus-field-label">
            {label}
            {required && <span style={{ color: 'var(--accent-competitor)', marginLeft: '4px' }}>*</span>}
          </label>
        </div>
      )}

      <input
        ref={ref}
        id={inputId}
        disabled={disabled}
        aria-invalid={Boolean(error)}
        aria-describedby={helperText || error ? helperId : undefined}
        className={`nexus-input ${className}`.trim()}
        {...props}
      />

      {(error || helperText) && (
        <span
          id={helperId}
          className={`nexus-field-helper ${error ? 'nexus-field-helper--error' : ''}`}
        >
          {error || helperText}
        </span>
      )}
    </div>
  );
});

export default Input;
