import React from 'react';

function Tick({ pos, ink }) {
  const [v, h] = pos.split('-');
  const s = { position: 'absolute', width: 'var(--tick)', height: 'var(--tick)', pointerEvents: 'none',
    [v]: 'var(--u-4)', [h]: 'var(--u-4)',
    borderTop: v === 'top' ? '1px solid ' + ink : undefined, borderBottom: v === 'bottom' ? '1px solid ' + ink : undefined,
    borderLeft: h === 'left' ? '1px solid ' + ink : undefined, borderRight: h === 'right' ? '1px solid ' + ink : undefined };
  return <span aria-hidden="true" style={s} />;
}

export function Plate({ corners = true, tone = 'light', pad = 'var(--u-8)', border = true, children, style, className, ...rest }) {
  const ink = tone === 'dark' ? 'var(--rule-onyx)' : 'var(--rule)';
  return (
    <div className={className} style={{ position: 'relative', padding: pad, outline: border ? '1px solid ' + (tone === 'dark' ? 'var(--rule-onyx)' : 'var(--rule-faint)') : 'none',
      outlineOffset: '-1px', height: '100%', ...style }} {...rest}>
      {corners ? ['top-left', 'top-right', 'bottom-left', 'bottom-right'].map(p => <Tick key={p} pos={p} ink={tone === 'dark' ? 'rgba(10,10,10,0.45)' : 'var(--rule-strong)'} />) : null}
      {children}
    </div>
  );
}
