import { useRef, useEffect } from 'react';
import * as d3 from 'd3';

/**
 * Custom hook for integrating D3 visualizations with React
 * 
 * @template GElement - The element type for D3 selection (e.g., SVGSVGElement)
 * @template PDatum - The data type bound to the element
 * @template PGroup - The parent element type
 * @param renderFn - Function that contains D3 code to render the visualization
 * @param dependencies - Array of dependencies to trigger re-rendering
 * @returns React ref to attach to the DOM element for the visualization
 */
function useD3<
  GElement extends d3.BaseType, 
  PDatum = unknown, 
  PGroup extends d3.BaseType = d3.BaseType
>(
  renderFn: (selection: d3.Selection<GElement, PDatum, PGroup, unknown>) => void,
  dependencies: React.DependencyList = []
): React.RefObject<GElement> {
  const ref = useRef<GElement>(null);

  useEffect(() => {
    // Call the render function with the current DOM node
    if (ref.current) {
      renderFn(d3.select(ref.current) as d3.Selection<GElement, PDatum, PGroup, unknown>);
    }
    
    // Cleanup function to prevent memory leaks
    return () => {
      if (ref.current) {
        // Clean up any event listeners or timers D3 might have added
        d3.select(ref.current).selectAll('*').interrupt();
      }
    };
  }, dependencies);

  return ref;
}

/**
 * Specialized version of useD3 for SVG elements
 * 
 * @template PDatum - The data type bound to the element
 * @param renderFn - Function that contains D3 code to render the visualization
 * @param dependencies - Array of dependencies to trigger re-rendering
 * @returns React ref to attach to an SVG element
 */
export function useSvgD3<PDatum = unknown>(
  renderFn: (selection: d3.Selection<SVGSVGElement, PDatum, null, undefined>) => void,
  dependencies: React.DependencyList = []
): React.RefObject<SVGSVGElement> {
  return useD3<SVGSVGElement, PDatum, null>(renderFn, dependencies);
}

/**
 * Specialized version of useD3 for div elements
 * 
 * @template PDatum - The data type bound to the element
 * @param renderFn - Function that contains D3 code to render the visualization
 * @param dependencies - Array of dependencies to trigger re-rendering
 * @returns React ref to attach to a div element
 */
export function useDivD3<PDatum = unknown>(
  renderFn: (selection: d3.Selection<HTMLDivElement, PDatum, null, undefined>) => void,
  dependencies: React.DependencyList = []
): React.RefObject<HTMLDivElement> {
  return useD3<HTMLDivElement, PDatum, null>(renderFn, dependencies);
}

export default useD3;