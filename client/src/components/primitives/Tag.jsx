import React, { forwardRef } from 'react';

/**
 * Tag Primitive
 * Compact categorization tag with optional dismiss or interactive selection
 * States: default, hover, focus-visible (2px accent ring), selected
 */
export const Tag = forwardRef(function Tag(
  {
    children,
    selected = false,
    onDismiss,
    onClick,
    className = '',
    disabled = false,
    ...props
  },
  ref
) {
  const isInteractive = Boolean(onClick) && !disabled;
  const interactiveClass = isInteractive ? 'nexus-tag--interactive' : '';
  const selectedClass = selected ? 'nexus-tag--selected' : '';

  return (
    <span
      ref={ref}
      role={isInteractive ? 'button' : undefined}
      tabIndex={isInteractive ? 0 : undefined}
      onClick={isInteractive ? onClick : undefined}
      onKeyDown={
        isInteractive
          ? (e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                onClick(e);
              }
            }
          : undefined
      }
      className={`nexus-tag ${interactiveClass} ${selectedClass} ${className}`.trim()}
      {...props}
    >
      <span>{children}</span>
      {onDismiss && !disabled && (
        <button
          type="button"
          aria-label="Remove tag"
          onClick={(e) => {
            e.stopPropagation();
            onDismiss(e);
          }}
          className="nexus-tag-close-btn"
        >
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth="1.5">
            <path d="M3 3l6 6M9 3l-6 6" />
          </svg>
        </button>
      )}
    </span>
  );
});

export default Tag;
