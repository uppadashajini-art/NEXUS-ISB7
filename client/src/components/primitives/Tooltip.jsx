import React, { useState, useId } from 'react';

/**
 * Tooltip Primitive
 * Accessible tooltip with hover & focus-visible triggers
 * Position: 'top', 'bottom', 'left', 'right'
 * Motion: 150ms cubic-bezier(0.2, 0.8, 0.2, 1)
 */
export function Tooltip({
  content,
  children,
  position = 'top',
  className = '',
}) {
  const [visible, setVisible] = useState(false);
  const tooltipId = useId();

  if (!content) return children;

  return (
    <div
      className={`nexus-tooltip-wrapper ${className}`.trim()}
      onMouseEnter={() => setVisible(true)}
      onMouseLeave={() => setVisible(false)}
      onFocus={() => setVisible(true)}
      onBlur={() => setVisible(false)}
    >
      <div aria-describedby={visible ? tooltipId : undefined}>
        {children}
      </div>

      <div
        id={tooltipId}
        role="tooltip"
        className={`nexus-tooltip-content nexus-tooltip-content--${position} ${
          visible ? 'nexus-tooltip-content--visible' : ''
        }`.trim()}
      >
        {content}
      </div>
    </div>
  );
}

export default Tooltip;
