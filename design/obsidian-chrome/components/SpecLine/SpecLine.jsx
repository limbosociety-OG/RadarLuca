import React from 'react';

export function SpecLine({ label, value, rule = true, tone = 'light', style, className, ...rest }) {
  const ink = tone === 'dark' ? 'var(--ink-onyx)' : 'var(--ink-mid)';
  const inkStrong = tone === 'dark' ? 'var(--ink-onyx)' : 'var(--ink-full)';
  return (
    <div className={className} style={{ display: 'flex', alignItems: 'baseline', gap: 'var(--u-4)', ...style }} {...rest}>
      <span style={{ fontFamily: 'var(--face-spec)', fontWeight: 'var(--w-micro)', fontSize: 'var(--s-micro)',
        letterSpacing: 'var(--tr-micro)', textTransform: 'uppercase', color: ink, whiteSpace: 'nowrap' }}>{label}</span>
      {rule ? <span aria-hidden="true" style={{ flex: 1, height: 1, background: tone === 'dark' ? 'var(--rule-onyx)' : 'var(--rule)' }} /> : null}
      {value != null ? <span style={{ fontFamily: 'var(--face-spec)', fontWeight: 'var(--w-micro)', fontSize: 'var(--s-micro)',
        letterSpacing: 'var(--tr-micro)', textTransform: 'uppercase', color: inkStrong, whiteSpace: 'nowrap' }}>{value}</span> : null}
    </div>
  );
}
