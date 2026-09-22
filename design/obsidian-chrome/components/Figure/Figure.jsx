import React from 'react';

const SIZES = { lg: 'clamp(72px, 12vw, 216px)', md: 'clamp(52px, 8vw, 132px)', sm: 'clamp(36px, 5vw, 76px)' };

export function Figure({ value, unit, label, size = 'md', tone = 'light', style, className, ...rest }) {
  const ink = tone === 'dark' ? 'var(--ink-onyx)' : 'var(--ink-full)';
  const sub = tone === 'dark' ? 'var(--ink-onyx-mid)' : 'var(--ink-mid)';
  return (
    <div className={className} style={{ color: ink, ...style }} {...rest}>
      <div style={{ fontFamily: 'var(--face-display)', fontWeight: 'var(--w-display-thin)', fontSize: SIZES[size],
        letterSpacing: 'var(--tr-figure)', lineHeight: 0.86, display: 'flex', alignItems: 'flex-start', gap: '0.08em' }}>
        <span>{value}</span>
        {unit ? <span style={{ fontSize: '0.28em', fontWeight: 300, letterSpacing: '0', marginTop: '0.3em' }}>{unit}</span> : null}
      </div>
      {label ? <div style={{ marginTop: 'var(--u-4)', fontFamily: 'var(--face-spec)', fontWeight: 'var(--w-micro)',
        fontSize: 'var(--s-micro)', letterSpacing: 'var(--tr-micro)', textTransform: 'uppercase', color: sub }}>{label}</div> : null}
    </div>
  );
}
