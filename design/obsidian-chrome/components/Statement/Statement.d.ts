export interface StatementProps {
  level?: 'hero' | 'display' | 'statement' | 'lead' | 'caps' | 'ring';
  /** Element tag to render. */
  as?: string;
  caps?: boolean;
  tone?: 'light' | 'dark';
  /** max-width, e.g. "var(--measure-body)". */
  measure?: string;
  children?: React.ReactNode;
  style?: React.CSSProperties;
  className?: string;
}

export declare function Statement(props: StatementProps): JSX.Element;
