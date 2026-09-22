export interface FieldProps {
  /** Directional light field sampled from the reference boards. */
  variant?: 'blob' | 'wash' | 'cone' | 'corner' | 'sky' | 'horizon' | 'onyx' | 'slab' | 'paper';
  /** Darkening pass so type never sits on the bright zone. */
  veil?: 'none' | 'bottom' | 'top' | 'left';
  /** CSS aspect-ratio, e.g. "4 / 5". */
  ratio?: string;
  pad?: string;
  children?: React.ReactNode;
  style?: React.CSSProperties;
  className?: string;
}

export declare function Field(props: FieldProps): JSX.Element;
