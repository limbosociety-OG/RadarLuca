import React from 'react';

const LEVELS = {
  hero:      { fontSize: 'clamp(44px, 7vw, 132px)', lineHeight: 'var(--lh-hero)', letterSpacing: 'var(--tr-hero)', fontWeight: 200, family: 'var(--face-display)' },
  display:   { fontSize: 'clamp(34px, 5vw, 92px)', lineHeight: 'var(--lh-display)', letterSpacing: 'var(--tr-display)', fontWeight: 300, family: 'var(--face-display)' },
  statement: { fontSize: 'clamp(26px, 3.6vw, 68px)', lineHeight: 'var(--lh-statement)', letterSpacing: 'var(--tr-display)', fontWeight: 300, family: 'var(--face-display)' },
  lead:      { fontSize: 'clamp(17px, 1.6vw, 22px)', lineHeight: 'var(--lh-text)', letterSpacing: 'var(--tr-text)', fontWeight: 400, family: 'var(--face-text)' },
  caps:      { fontSize: 'var(--s-spec)', lineHeight: 'var(--lh-spec)', letterSpacing: 'var(--tr-micro)', fontWeight: 500, family: 'var(--face-spec)' },
  ring:      { fontSize: 'clamp(22px, 2.4vw, 34px)', lineHeight: 1.3, letterSpacing: '0.04em', fontWeight: 400, family: 'var(--face-ring)' }
};

export function Statement({ level = 'display', as = 'div', caps, tone = 'light', measure, children, style, className, ...rest }) {
  const L = LEVELS[level] || LEVELS.display;
  const Tag = as;
  return (
    <Tag className={className} style={{ fontFamily: L.family, fontSize: L.fontSize, lineHeight: L.lineHeight,
      letterSpacing: L.letterSpacing, fontWeight: L.fontWeight, textTransform: caps || level === 'caps' ? 'uppercase' : undefined,
      color: tone === 'dark' ? 'var(--ink-onyx)' : 'var(--ink-full)', maxWidth: measure, textWrap: 'pretty', ...style }} {...rest}>{children}</Tag>
  );
}
