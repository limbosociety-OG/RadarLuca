import React from 'react';

const BASE_FS = 6.2;
const MIN_GAP = 0.08;

function useFit(text, arc, gap) {
  const ref = React.useRef(null);
  const [fit, setFit] = React.useState({ fs: BASE_FS, gap });
  React.useLayoutEffect(() => {
    const el = ref.current;
    if (!el || !text) return;
    let len;
    try { len = el.getComputedTextLength(); } catch (e) { return; }
    if (!len) return;
    const n = text.length;
    const glyphs = len - n * gap * BASE_FS;
    let fs = BASE_FS, g = gap;
    if (len > arc) {
      const tight = glyphs + n * MIN_GAP * BASE_FS;
      if (tight <= arc) g = Math.max(MIN_GAP, (arc - glyphs) / (n * BASE_FS));
      else { g = MIN_GAP; fs = BASE_FS * (arc / tight); }
    }
    setFit(p => (Math.abs(p.fs - fs) < 0.01 && Math.abs(p.gap - g) < 0.005 ? p : { fs, gap: g }));
  }, [text, gap, arc]);
  return [ref, fit];
}

export function Seal({ ring, ringBottom, mark, size = 168, shape = 'circle', tone = 'light', weight = 1, gap = 0.24, innerRing = false, openGap = 0, dim = 1, style, className, ...rest }) {
  size = Number(size) || 168; weight = Number(weight) || 1; gap = Number(gap) || 0.24;
  const id = React.useId().replace(/:/g, '');
  const ink = tone === 'dark' ? 'var(--ink-onyx)' : 'var(--ink-full)';
  const oval = shape === 'oval';
  openGap = Number(openGap) || 0; dim = dim === undefined ? 1 : Number(dim);
  const rx = oval ? 38 : 48, ry = 48;
  const top = ring ? ring.toUpperCase() : null;
  const bottom = ringBottom ? ringBottom.toUpperCase() : null;
  const trx = rx - 9, try_ = ry - 9, brx = rx - 3.5, bry = ry - 3.5;
  const [topRef, topFit] = useFit(top, Math.PI * ((trx + try_) / 2) * 0.94, gap);
  const [botRef, botFit] = useFit(bottom, Math.PI * ((brx + bry) / 2) * 0.86, gap);
  const lines = String(mark ?? '').split(/\n|\|/).filter(Boolean);
  const markFs = size * (oval ? 0.3 : 0.34) / Math.max(1, lines.length * 0.72);

  return (
    <div className={className} style={{ position: 'relative', width: size, height: size, flex: '0 0 auto', opacity: dim, ...style }} {...rest}>
      <svg viewBox="0 0 100 100" width={size} height={size} style={{ display: 'block', position: 'absolute', inset: 0 }} aria-hidden="true">
        {openGap > 0 ? (() => {
          // an interrupted ring: the device reads as a drawn arc, not a stamp
          const a = (openGap / 2) * Math.PI / 180, big = openGap < 180 ? 1 : 0;
          const x1 = 50 + rx * Math.sin(a), y1 = 50 + ry * Math.cos(a);
          const x2 = 50 - rx * Math.sin(a), y2 = y1;
          return <path d={'M ' + x1 + ',' + y1 + ' A ' + rx + ',' + ry + ' 0 ' + big + ' 0 ' + x2 + ',' + y2} fill="none" stroke={ink} strokeWidth={weight} strokeLinecap="round" />;
        })() : <ellipse cx="50" cy="50" rx={rx} ry={ry} fill="none" stroke={ink} strokeWidth={weight} />}
        {innerRing ? <ellipse cx="50" cy="50" rx={rx - 3} ry={ry - 3} fill="none" stroke={ink} strokeWidth={weight * 0.5} /> : null}
        <defs>
          <path id={'t' + id} fill="none" d={'M ' + (50 - trx) + ',50 A ' + trx + ',' + try_ + ' 0 0 1 ' + (50 + trx) + ',50'} />
          <path id={'b' + id} fill="none" d={'M ' + (50 - brx) + ',50 A ' + brx + ',' + bry + ' 0 0 0 ' + (50 + brx) + ',50'} />
        </defs>
        {top ? (<>
          <text ref={topRef} x="0" y="-200" fill="none" style={{ fontFamily: 'var(--face-spec)', fontSize: BASE_FS, fontWeight: 500, letterSpacing: gap + 'em' }}>{top}</text>
          <text fill={ink} style={{ fontFamily: 'var(--face-spec)', fontSize: topFit.fs, fontWeight: 500, letterSpacing: topFit.gap + 'em' }}>
            <textPath href={'#t' + id} startOffset="50%" textAnchor="middle">{top}</textPath>
          </text>
        </>) : null}
        {bottom ? (<>
          <text ref={botRef} x="0" y="-200" fill="none" style={{ fontFamily: 'var(--face-spec)', fontSize: BASE_FS, fontWeight: 500, letterSpacing: gap + 'em' }}>{bottom}</text>
          <text fill={ink} style={{ fontFamily: 'var(--face-spec)', fontSize: botFit.fs, fontWeight: 500, letterSpacing: botFit.gap + 'em' }}>
            <textPath href={'#b' + id} startOffset="50%" textAnchor="middle">{bottom}</textPath>
          </text>
        </>) : null}
      </svg>
      <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: ink,
        fontFamily: 'var(--face-ring)', fontWeight: 500, letterSpacing: '0.02em', fontSize: markFs, lineHeight: 0.82 }}>
        {lines.map((l, i) => <span key={i}>{l}</span>)}
      </div>
    </div>
  );
}
