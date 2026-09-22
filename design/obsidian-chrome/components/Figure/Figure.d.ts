export interface FigureProps {
  /** The numeral itself — set light and oversized. */
  value: React.ReactNode;
  /** Small trailing unit (%, §, dias). */
  unit?: string;
  label?: string;
  size?: 'lg' | 'md' | 'sm';
  tone?: 'light' | 'dark';
  style?: React.CSSProperties;
  className?: string;
}

export declare function Figure(props: FigureProps): JSX.Element;
