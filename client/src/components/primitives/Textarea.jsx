import React, { forwardRef, useId } from 'react';

/**
 * Textarea Primitive
 * States: default, hover, focus-visible (2px accent ring), disabled, error
 */
export const Textarea = forwardRef(function Textarea(
  {
    label,
    error,
    helperText,
    id,
    disabled = false,
    className = '',
    required = false,
    rows = 4,
    ...props
  },
  ref
) {
  const generatedId = useId();
  const textareaId = id || generatedId;
  const helperId = `${textareaId}-helper`;

  return (
    <div className={`nexus-field-container ${error ? 'nexus-field--error' : ''}`}>
      {label && (
        <div className="nexus-field-header">
          <label htmlFor={textareaId} className="nexus-field-label">
            {label}
            {required && <span style={{ color: 'var(--accent-competitor)', marginLeft: '4px' }}>*</span>}
          </label>
        </div>
      )}

      <textarea
        ref={ref}
        id={textareaId}
        rows={rows}
        disabled={disabled}
        aria-invalid={Boolean(error)}
        aria-describedby={helperText || error ? helperId : undefined}
        className={`nexus-textarea ${className}`.trim()}
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

export default Textarea;
