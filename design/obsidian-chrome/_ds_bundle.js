/* @ds-bundle: {"format":4,"namespace":"LucaMartinsDesignSystem_f910c3","components":[{"name":"Field","sourcePath":"components/Field/Field.jsx"},{"name":"Figure","sourcePath":"components/Figure/Figure.jsx"},{"name":"Mosaic","sourcePath":"components/Mosaic/Mosaic.jsx"},{"name":"Tile","sourcePath":"components/Mosaic/Mosaic.jsx"},{"name":"Plate","sourcePath":"components/Plate/Plate.jsx"},{"name":"Seal","sourcePath":"components/Seal/Seal.jsx"},{"name":"SpecLine","sourcePath":"components/SpecLine/SpecLine.jsx"},{"name":"Statement","sourcePath":"components/Statement/Statement.jsx"}],"sourceHashes":{"components/Field/Field.jsx":"ed6eed8e213c","components/Figure/Figure.jsx":"137a14525372","components/Mosaic/Mosaic.jsx":"52c9ac087972","components/Plate/Plate.jsx":"ca3e29dfb541","components/Seal/Seal.jsx":"0a427ca8b6c1","components/SpecLine/SpecLine.jsx":"e249e3f20219","components/Statement/Statement.jsx":"ef2dd70e615c"},"inlinedExternals":[],"unexposedExports":[]} */

(() => {

const __ds_ns = (window.LucaMartinsDesignSystem_f910c3 = window.LucaMartinsDesignSystem_f910c3 || {});

const __ds_scope = {};

(__ds_ns.__errors = __ds_ns.__errors || []);

// components/Field/Field.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const FIELDS = {
  blob: 'var(--field-blob)',
  wash: 'var(--field-wash)',
  cone: 'var(--field-cone)',
  corner: 'var(--field-corner)',
  sky: 'var(--field-sky)',
  horizon: 'var(--field-horizon)',
  onyx: 'var(--field-onyx)',
  slab: 'var(--field-slab)',
  paper: 'var(--field-paper)'
};
const VEILS = {
  none: null,
  bottom: 'var(--veil-bottom)',
  top: 'var(--veil-top)',
  left: 'var(--veil-left)'
};
function Field({
  variant = 'blob',
  veil = 'none',
  ratio,
  pad,
  children,
  style,
  className,
  ...rest
}) {
  const paper = variant === 'paper';
  return /*#__PURE__*/React.createElement("div", _extends({
    className: className,
    style: {
      position: 'relative',
      overflow: 'hidden',
      background: FIELDS[variant] || FIELDS.blob,
      color: paper ? 'var(--ink-onyx)' : 'var(--ink-high)',
      aspectRatio: ratio,
      padding: pad,
      isolation: 'isolate',
      ...style
    }
  }, rest), VEILS[veil] ? /*#__PURE__*/React.createElement("div", {
    "aria-hidden": "true",
    style: {
      position: 'absolute',
      inset: 0,
      background: VEILS[veil],
      pointerEvents: 'none'
    }
  }) : null, /*#__PURE__*/React.createElement("div", {
    style: {
      position: 'relative',
      height: '100%'
    }
  }, children));
}
Object.assign(__ds_scope, { Field });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/Field/Field.jsx", error: String((e && e.message) || e) }); }

// components/Figure/Figure.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const SIZES = {
  lg: 'clamp(72px, 12vw, 216px)',
  md: 'clamp(52px, 8vw, 132px)',
  sm: 'clamp(36px, 5vw, 76px)'
};
function Figure({
  value,
  unit,
  label,
  size = 'md',
  tone = 'light',
  style,
  className,
  ...rest
}) {
  const ink = tone === 'dark' ? 'var(--ink-onyx)' : 'var(--ink-full)';
  const sub = tone === 'dark' ? 'var(--ink-onyx-mid)' : 'var(--ink-mid)';
  return /*#__PURE__*/React.createElement("div", _extends({
    className: className,
    style: {
      color: ink,
      ...style
    }
  }, rest), /*#__PURE__*/React.createElement("div", {
    style: {
      fontFamily: 'var(--face-display)',
      fontWeight: 'var(--w-display-thin)',
      fontSize: SIZES[size],
      letterSpacing: 'var(--tr-figure)',
      lineHeight: 0.86,
      display: 'flex',
      alignItems: 'flex-start',
      gap: '0.08em'
    }
  }, /*#__PURE__*/React.createElement("span", null, value), unit ? /*#__PURE__*/React.createElement("span", {
    style: {
      fontSize: '0.28em',
      fontWeight: 300,
      letterSpacing: '0',
      marginTop: '0.3em'
    }
  }, unit) : null), label ? /*#__PURE__*/React.createElement("div", {
    style: {
      marginTop: 'var(--u-4)',
      fontFamily: 'var(--face-spec)',
      fontWeight: 'var(--w-micro)',
      fontSize: 'var(--s-micro)',
      letterSpacing: 'var(--tr-micro)',
      textTransform: 'uppercase',
      color: sub
    }
  }, label) : null);
}
Object.assign(__ds_scope, { Figure });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/Figure/Figure.jsx", error: String((e && e.message) || e) }); }

// components/Mosaic/Mosaic.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
function Mosaic({
  cols = 12,
  rows,
  gap = 'var(--gutter-mosaic)',
  children,
  style,
  className,
  ...rest
}) {
  return /*#__PURE__*/React.createElement("div", _extends({
    className: className,
    style: {
      display: 'grid',
      gridTemplateColumns: 'repeat(' + cols + ', minmax(0, 1fr))',
      gridAutoRows: rows ? undefined : 'minmax(0, auto)',
      gridTemplateRows: rows,
      gap,
      ...style
    }
  }, rest), children);
}
function Tile({
  span = 4,
  rowSpan = 1,
  children,
  style,
  className,
  ...rest
}) {
  return /*#__PURE__*/React.createElement("div", _extends({
    className: className,
    style: {
      gridColumn: 'span ' + span,
      gridRow: 'span ' + rowSpan,
      minWidth: 0,
      position: 'relative',
      ...style
    }
  }, rest), children);
}
Object.assign(__ds_scope, { Mosaic, Tile });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/Mosaic/Mosaic.jsx", error: String((e && e.message) || e) }); }

// components/Plate/Plate.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
function Tick({
  pos,
  ink
}) {
  const [v, h] = pos.split('-');
  const s = {
    position: 'absolute',
    width: 'var(--tick)',
    height: 'var(--tick)',
    pointerEvents: 'none',
    [v]: 'var(--u-4)',
    [h]: 'var(--u-4)',
    borderTop: v === 'top' ? '1px solid ' + ink : undefined,
    borderBottom: v === 'bottom' ? '1px solid ' + ink : undefined,
    borderLeft: h === 'left' ? '1px solid ' + ink : undefined,
    borderRight: h === 'right' ? '1px solid ' + ink : undefined
  };
  return /*#__PURE__*/React.createElement("span", {
    "aria-hidden": "true",
    style: s
  });
}
function Plate({
  corners = true,
  tone = 'light',
  pad = 'var(--u-8)',
  border = true,
  children,
  style,
  className,
  ...rest
}) {
  const ink = tone === 'dark' ? 'var(--rule-onyx)' : 'var(--rule)';
  return /*#__PURE__*/React.createElement("div", _extends({
    className: className,
    style: {
      position: 'relative',
      padding: pad,
      outline: border ? '1px solid ' + (tone === 'dark' ? 'var(--rule-onyx)' : 'var(--rule-faint)') : 'none',
      outlineOffset: '-1px',
      height: '100%',
      ...style
    }
  }, rest), corners ? ['top-left', 'top-right', 'bottom-left', 'bottom-right'].map(p => /*#__PURE__*/React.createElement(Tick, {
    key: p,
    pos: p,
    ink: tone === 'dark' ? 'rgba(10,10,10,0.45)' : 'var(--rule-strong)'
  })) : null, children);
}
Object.assign(__ds_scope, { Plate });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/Plate/Plate.jsx", error: String((e && e.message) || e) }); }

// components/Seal/Seal.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const BASE_FS = 6.2;
const MIN_GAP = 0.08;
function useFit(text, arc, gap) {
  const ref = React.useRef(null);
  const [fit, setFit] = React.useState({
    fs: BASE_FS,
    gap
  });
  React.useLayoutEffect(() => {
    const el = ref.current;
    if (!el || !text) return;
    let len;
    try {
      len = el.getComputedTextLength();
    } catch (e) {
      return;
    }
    if (!len) return;
    const n = text.length;
    const glyphs = len - n * gap * BASE_FS;
    let fs = BASE_FS,
      g = gap;
    if (len > arc) {
      const tight = glyphs + n * MIN_GAP * BASE_FS;
      if (tight <= arc) g = Math.max(MIN_GAP, (arc - glyphs) / (n * BASE_FS));else {
        g = MIN_GAP;
        fs = BASE_FS * (arc / tight);
      }
    }
    setFit(p => Math.abs(p.fs - fs) < 0.01 && Math.abs(p.gap - g) < 0.005 ? p : {
      fs,
      gap: g
    });
  }, [text, gap, arc]);
  return [ref, fit];
}
function Seal({
  ring,
  ringBottom,
  mark,
  size = 168,
  shape = 'circle',
  tone = 'light',
  weight = 1,
  gap = 0.24,
  innerRing = false,
  openGap = 0,
  dim = 1,
  style,
  className,
  ...rest
}) {
  size = Number(size) || 168;
  weight = Number(weight) || 1;
  gap = Number(gap) || 0.24;
  const id = React.useId().replace(/:/g, '');
  const ink = tone === 'dark' ? 'var(--ink-onyx)' : 'var(--ink-full)';
  const oval = shape === 'oval';
  openGap = Number(openGap) || 0;
  dim = dim === undefined ? 1 : Number(dim);
  const rx = oval ? 38 : 48,
    ry = 48;
  const top = ring ? ring.toUpperCase() : null;
  const bottom = ringBottom ? ringBottom.toUpperCase() : null;
  const trx = rx - 9,
    try_ = ry - 9,
    brx = rx - 3.5,
    bry = ry - 3.5;
  const [topRef, topFit] = useFit(top, Math.PI * ((trx + try_) / 2) * 0.94, gap);
  const [botRef, botFit] = useFit(bottom, Math.PI * ((brx + bry) / 2) * 0.86, gap);
  const lines = String(mark ?? '').split(/\n|\|/).filter(Boolean);
  const markFs = size * (oval ? 0.3 : 0.34) / Math.max(1, lines.length * 0.72);
  return /*#__PURE__*/React.createElement("div", _extends({
    className: className,
    style: {
      position: 'relative',
      width: size,
      height: size,
      flex: '0 0 auto',
      opacity: dim,
      ...style
    }
  }, rest), /*#__PURE__*/React.createElement("svg", {
    viewBox: "0 0 100 100",
    width: size,
    height: size,
    style: {
      display: 'block',
      position: 'absolute',
      inset: 0
    },
    "aria-hidden": "true"
  }, openGap > 0 ? (() => {
    // an interrupted ring: the device reads as a drawn arc, not a stamp
    const a = openGap / 2 * Math.PI / 180,
      big = openGap < 180 ? 1 : 0;
    const x1 = 50 + rx * Math.sin(a),
      y1 = 50 + ry * Math.cos(a);
    const x2 = 50 - rx * Math.sin(a),
      y2 = y1;
    return /*#__PURE__*/React.createElement("path", {
      d: 'M ' + x1 + ',' + y1 + ' A ' + rx + ',' + ry + ' 0 ' + big + ' 0 ' + x2 + ',' + y2,
      fill: "none",
      stroke: ink,
      strokeWidth: weight,
      strokeLinecap: "round"
    });
  })() : /*#__PURE__*/React.createElement("ellipse", {
    cx: "50",
    cy: "50",
    rx: rx,
    ry: ry,
    fill: "none",
    stroke: ink,
    strokeWidth: weight
  }), innerRing ? /*#__PURE__*/React.createElement("ellipse", {
    cx: "50",
    cy: "50",
    rx: rx - 3,
    ry: ry - 3,
    fill: "none",
    stroke: ink,
    strokeWidth: weight * 0.5
  }) : null, /*#__PURE__*/React.createElement("defs", null, /*#__PURE__*/React.createElement("path", {
    id: 't' + id,
    fill: "none",
    d: 'M ' + (50 - trx) + ',50 A ' + trx + ',' + try_ + ' 0 0 1 ' + (50 + trx) + ',50'
  }), /*#__PURE__*/React.createElement("path", {
    id: 'b' + id,
    fill: "none",
    d: 'M ' + (50 - brx) + ',50 A ' + brx + ',' + bry + ' 0 0 0 ' + (50 + brx) + ',50'
  })), top ? /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement("text", {
    ref: topRef,
    x: "0",
    y: "-200",
    fill: "none",
    style: {
      fontFamily: 'var(--face-spec)',
      fontSize: BASE_FS,
      fontWeight: 500,
      letterSpacing: gap + 'em'
    }
  }, top), /*#__PURE__*/React.createElement("text", {
    fill: ink,
    style: {
      fontFamily: 'var(--face-spec)',
      fontSize: topFit.fs,
      fontWeight: 500,
      letterSpacing: topFit.gap + 'em'
    }
  }, /*#__PURE__*/React.createElement("textPath", {
    href: '#t' + id,
    startOffset: "50%",
    textAnchor: "middle"
  }, top))) : null, bottom ? /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement("text", {
    ref: botRef,
    x: "0",
    y: "-200",
    fill: "none",
    style: {
      fontFamily: 'var(--face-spec)',
      fontSize: BASE_FS,
      fontWeight: 500,
      letterSpacing: gap + 'em'
    }
  }, bottom), /*#__PURE__*/React.createElement("text", {
    fill: ink,
    style: {
      fontFamily: 'var(--face-spec)',
      fontSize: botFit.fs,
      fontWeight: 500,
      letterSpacing: botFit.gap + 'em'
    }
  }, /*#__PURE__*/React.createElement("textPath", {
    href: '#b' + id,
    startOffset: "50%",
    textAnchor: "middle"
  }, bottom))) : null), /*#__PURE__*/React.createElement("div", {
    style: {
      position: 'absolute',
      inset: 0,
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      color: ink,
      fontFamily: 'var(--face-ring)',
      fontWeight: 500,
      letterSpacing: '0.02em',
      fontSize: markFs,
      lineHeight: 0.82
    }
  }, lines.map((l, i) => /*#__PURE__*/React.createElement("span", {
    key: i
  }, l))));
}
Object.assign(__ds_scope, { Seal });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/Seal/Seal.jsx", error: String((e && e.message) || e) }); }

// components/SpecLine/SpecLine.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
function SpecLine({
  label,
  value,
  rule = true,
  tone = 'light',
  style,
  className,
  ...rest
}) {
  const ink = tone === 'dark' ? 'var(--ink-onyx)' : 'var(--ink-mid)';
  const inkStrong = tone === 'dark' ? 'var(--ink-onyx)' : 'var(--ink-full)';
  return /*#__PURE__*/React.createElement("div", _extends({
    className: className,
    style: {
      display: 'flex',
      alignItems: 'baseline',
      gap: 'var(--u-4)',
      ...style
    }
  }, rest), /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--face-spec)',
      fontWeight: 'var(--w-micro)',
      fontSize: 'var(--s-micro)',
      letterSpacing: 'var(--tr-micro)',
      textTransform: 'uppercase',
      color: ink,
      whiteSpace: 'nowrap'
    }
  }, label), rule ? /*#__PURE__*/React.createElement("span", {
    "aria-hidden": "true",
    style: {
      flex: 1,
      height: 1,
      background: tone === 'dark' ? 'var(--rule-onyx)' : 'var(--rule)'
    }
  }) : null, value != null ? /*#__PURE__*/React.createElement("span", {
    style: {
      fontFamily: 'var(--face-spec)',
      fontWeight: 'var(--w-micro)',
      fontSize: 'var(--s-micro)',
      letterSpacing: 'var(--tr-micro)',
      textTransform: 'uppercase',
      color: inkStrong,
      whiteSpace: 'nowrap'
    }
  }, value) : null);
}
Object.assign(__ds_scope, { SpecLine });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/SpecLine/SpecLine.jsx", error: String((e && e.message) || e) }); }

// components/Statement/Statement.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
const LEVELS = {
  hero: {
    fontSize: 'clamp(44px, 7vw, 132px)',
    lineHeight: 'var(--lh-hero)',
    letterSpacing: 'var(--tr-hero)',
    fontWeight: 200,
    family: 'var(--face-display)'
  },
  display: {
    fontSize: 'clamp(34px, 5vw, 92px)',
    lineHeight: 'var(--lh-display)',
    letterSpacing: 'var(--tr-display)',
    fontWeight: 300,
    family: 'var(--face-display)'
  },
  statement: {
    fontSize: 'clamp(26px, 3.6vw, 68px)',
    lineHeight: 'var(--lh-statement)',
    letterSpacing: 'var(--tr-display)',
    fontWeight: 300,
    family: 'var(--face-display)'
  },
  lead: {
    fontSize: 'clamp(17px, 1.6vw, 22px)',
    lineHeight: 'var(--lh-text)',
    letterSpacing: 'var(--tr-text)',
    fontWeight: 400,
    family: 'var(--face-text)'
  },
  caps: {
    fontSize: 'var(--s-spec)',
    lineHeight: 'var(--lh-spec)',
    letterSpacing: 'var(--tr-micro)',
    fontWeight: 500,
    family: 'var(--face-spec)'
  },
  ring: {
    fontSize: 'clamp(22px, 2.4vw, 34px)',
    lineHeight: 1.3,
    letterSpacing: '0.04em',
    fontWeight: 400,
    family: 'var(--face-ring)'
  }
};
function Statement({
  level = 'display',
  as = 'div',
  caps,
  tone = 'light',
  measure,
  children,
  style,
  className,
  ...rest
}) {
  const L = LEVELS[level] || LEVELS.display;
  const Tag = as;
  return /*#__PURE__*/React.createElement(Tag, _extends({
    className: className,
    style: {
      fontFamily: L.family,
      fontSize: L.fontSize,
      lineHeight: L.lineHeight,
      letterSpacing: L.letterSpacing,
      fontWeight: L.fontWeight,
      textTransform: caps || level === 'caps' ? 'uppercase' : undefined,
      color: tone === 'dark' ? 'var(--ink-onyx)' : 'var(--ink-full)',
      maxWidth: measure,
      textWrap: 'pretty',
      ...style
    }
  }, rest), children);
}
Object.assign(__ds_scope, { Statement });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/Statement/Statement.jsx", error: String((e && e.message) || e) }); }

__ds_ns.Field = __ds_scope.Field;

__ds_ns.Figure = __ds_scope.Figure;

__ds_ns.Mosaic = __ds_scope.Mosaic;

__ds_ns.Tile = __ds_scope.Tile;

__ds_ns.Plate = __ds_scope.Plate;

__ds_ns.Seal = __ds_scope.Seal;

__ds_ns.SpecLine = __ds_scope.SpecLine;

__ds_ns.Statement = __ds_scope.Statement;

})();
