import React from 'react';

const FIELDS = {
  blob: 'var(--field-blob)', wash: 'var(--field-wash)', cone: 'var(--field-cone)',
  corner: 'var(--field-corner)', sky: 'var(--field-sky)', horizon: 'var(--field-horizon)',
  onyx: 'var(--field-onyx)', slab: 'var(--field-slab)', paper: 'var(--field-paper)'
};
const VEILS = { none: null, bottom: 'var(--veil-bottom)', top: 'var(--veil-top)', left: 'var(--veil-left)' };

export function Field({ variant = 'blob', veil = 'none', ratio, pad, children, style, className, ...rest }) {
  const paper = variant === 'paper';
  return (
    <div className={className} style={{ position: 'relative', overflow: 'hidden', background: FIELDS[variant] || FIELDS.blob,
      color: paper ? 'var(--ink-onyx)' : 'var(--ink-high)', aspectRatio: ratio, padding: pad, isolation: 'isolate', ...style }} {...rest}>
      {VEILS[veil] ? <div aria-hidden="true" style={{ position: 'absolute', inset: 0, background: VEILS[veil], pointerEvents: 'none' }} /> : null}
      <div style={{ position: 'relative', height: '100%' }}>{children}</div>
    </div>
  );
}
