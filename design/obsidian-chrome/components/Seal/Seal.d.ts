export interface SealProps {
  /** Copy on the upper arc; rendered in caps and auto-fitted. */
  ring?: string;
  /** Copy on the lower arc, set upright. */
  ringBottom?: string;
  /** Centre mark — stack lines with "\n" or "|" (e.g. "MA|D"). */
  mark?: React.ReactNode;
  /** Diameter in px. */
  size?: number;
  shape?: 'circle' | 'oval';
  tone?: 'light' | 'dark';
  /** Ring stroke weight in viewBox units. */
  weight?: number;
  /** Ring letter-spacing in em (auto-tightened when copy is long). */
  gap?: number;
  /** Second concentric hairline inside the ring. */
  innerRing?: boolean;
  /** Degrees of ring left open at the bottom — an abstract arc instead of a closed stamp. */
  openGap?: number;
  /** Overall opacity, for a quieter, more atmospheric device. */
  dim?: number;
  style?: React.CSSProperties;
  className?: string;
}

export declare function Seal(props: SealProps): JSX.Element;
