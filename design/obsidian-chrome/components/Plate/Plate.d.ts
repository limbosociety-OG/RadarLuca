export interface PlateProps {
  /** Registration ticks in all four corners. */
  corners?: boolean;
  tone?: 'light' | 'dark';
  pad?: string;
  border?: boolean;
  children?: React.ReactNode;
  style?: React.CSSProperties;
  className?: string;
}

export declare function Plate(props: PlateProps): JSX.Element;
