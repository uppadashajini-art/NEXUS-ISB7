import React, { forwardRef } from 'react';

/**
 * Card Primitive
 * Variants: 'surface' (#121217), 'surface-2' (#17171E)
 * Elevation: 1 (subtle), 2 (mid), 3 (deep architectural)
 * Padding: 'none', 'sm', 'md', 'lg'
 */
export const Card = forwardRef(function Card(
  {
    variant = 'surface',
    elevation = 1,
    padding = 'md',
    className = '',
    children,
    ...props
  },
  ref
) {
  const surfaceClass = variant === 'surface-2' ? 'nexus-card--surface-2' : '';
  const elevationClass = `nexus-card--elevated-${elevation}`;
  const paddingClass = `nexus-card--p-${padding}`;

  return (
    <div
      ref={ref}
      className={`nexus-card ${surfaceClass} ${elevationClass} ${paddingClass} ${className}`.trim()}
      {...props}
    >
      {children}
    </div>
  );
});

export default Card;
