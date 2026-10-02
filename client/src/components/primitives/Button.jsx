import React, { forwardRef } from 'react';

/**
 * Button Primitive
 * Variants: 'primary' (brand gradient), 'secondary', 'ghost'
 * Sizes: 'sm', 'md', 'lg'
 * States: hover, focus-visible (2px accent ring), disabled, active
 */
export const Button = forwardRef(function Button(
  {
    variant = 'secondary',
    size = 'md',
    disabled = false,
    className = '',
    children,
    type = 'button',
    ...props
  },
  ref
) {
  const variantClass = `nexus-btn--${variant}`;
  const sizeClass = `nexus-btn--${size}`;

  return (
    <button
      ref={ref}
      type={type}
      disabled={disabled}
      aria-disabled={disabled}
      className={`nexus-btn ${variantClass} ${sizeClass} ${className}`.trim()}
      {...props}
    >
      {children}
    </button>
  );
});

export default Button;
