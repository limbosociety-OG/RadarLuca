export interface SpecLineProps {
  label: string;
  value?: React.ReactNode;
  /** Hairline bridging label and value. */
  rule?: boolean;
  tone?: 'light' | 'dark';
  style?: React.CSSProperties;
  className?: string;
}

export declare function SpecLine(props: SpecLineProps): JSX.Element;
