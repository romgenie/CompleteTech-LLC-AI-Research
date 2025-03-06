import { useEffect, useRef } from 'react';
import * as d3 from 'd3';

export function useD3(renderChartFn: (svg: d3.Selection<SVGSVGElement, unknown, null, undefined>) => void, deps: any[] = []) {
  const ref = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (ref.current) {
      // Clear previous content
      d3.select(ref.current).selectAll('*').remove();
      // Render new chart
      renderChartFn(d3.select(ref.current));
    }
    return () => {};
  }, [renderChartFn, ...deps]);

  return ref;
}

// Alias for compatibility with code that uses useSvgD3
export const useSvgD3 = useD3;