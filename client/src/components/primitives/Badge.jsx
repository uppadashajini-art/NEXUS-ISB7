import React, { forwardRef } from 'react';

/**
 * Badge Primitive
 * Variants: 'idea' (#FFC72C), 'market' (#FF8A1F), 'customer' (#FF5A4E),
 *           'competitor' (#F23D5C), 'feasibility' (#2DD4BF), 'advisory' (#8B7CF6), 'neutral'
 * Typography: Label 11/16 600 uppercase tracking 0.08em
 */
export const Badge = forwardRef(function Badge(
  {
    variant = 'neutral',
    children,
    className = '',
    ...props
  },
  ref
) {
  const variantClass = `nexus-badge--${variant}`;

  return (
    <span
      ref={ref}
      className={`nexus-badge ${variantClass} ${className}`.trim()}
      {...props}
    >
      {children}
    </span>
  );
});

export default Badge;
