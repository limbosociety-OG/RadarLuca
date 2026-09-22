import React from 'react';

export function Mosaic({ cols = 12, rows, gap = 'var(--gutter-mosaic)', children, style, className, ...rest }) {
  return (
    <div className={className} style={{ display: 'grid', gridTemplateColumns: 'repeat(' + cols + ', minmax(0, 1fr))',
      gridAutoRows: rows ? undefined : 'minmax(0, auto)', gridTemplateRows: rows, gap, ...style }} {...rest}>{children}</div>
  );
}

export function Tile({ span = 4, rowSpan = 1, children, style, className, ...rest }) {
  return (
    <div className={className} style={{ gridColumn: 'span ' + span, gridRow: 'span ' + rowSpan, minWidth: 0, position: 'relative', ...style }} {...rest}>{children}</div>
  );
}
