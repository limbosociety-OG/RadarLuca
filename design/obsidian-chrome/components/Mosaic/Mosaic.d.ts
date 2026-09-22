export interface MosaicProps {
  cols?: number;
  /** grid-template-rows value, e.g. "repeat(6, 1fr)". */
  rows?: string;
  gap?: string;
  children?: React.ReactNode;
  style?: React.CSSProperties;
  className?: string;
}

export declare function Mosaic(props: MosaicProps): JSX.Element;

export interface TileProps {
  span?: number;
  rowSpan?: number;
  children?: React.ReactNode;
  style?: React.CSSProperties;
  className?: string;
}

export declare function Tile(props: TileProps): JSX.Element;
