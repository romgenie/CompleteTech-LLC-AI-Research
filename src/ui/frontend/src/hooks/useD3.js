import { useRef, useEffect } from 'react';
import * as d3 from 'd3';

/**
 * Custom hook for integrating D3 visualizations with React
 * 
 * @param {Function} renderChartFn - Function that contains D3 code to render the visualization
 * @param {Array} dependencies - Array of dependencies to trigger re-rendering
 * @returns {React.MutableRefObject} - Ref to attach to the DOM element for the visualization
 */
export function useD3(renderChartFn, dependencies = []) {
  const ref = useRef();

  useEffect(() => {
    // Call the render function with the current DOM node
    if (ref.current) {
      renderChartFn(d3.select(ref.current));
    }
    
    // Optional cleanup function to prevent memory leaks
    return () => {
      if (ref.current) {
        // Clean up any event listeners or timers D3 might have added
        d3.select(ref.current).selectAll('*').interrupt();
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, dependencies);

  return ref;
}

/**
 * Custom hook for SVG-based D3 visualizations
 * 
 * @param {Function} renderFn - Function that renders D3 visualization when called with a d3.Selection of an SVG element
 * @param {Array} dependencies - Dependencies array to control when to re-render
 * @returns {React.MutableRefObject} - Ref object to attach to an SVG element
 */
export function useSvgD3(renderFn, dependencies = []) {
  return useD3(renderFn, dependencies);
}

/**
 * Custom hook for div-based D3 visualizations
 * 
 * @param {Function} renderFn - Function that renders D3 visualization when called with a d3.Selection of a div element
 * @param {Array} dependencies - Dependencies array to control when to re-render
 * @returns {React.MutableRefObject} - Ref object to attach to a div element
 */
export function useDivD3(renderFn, dependencies = []) {
  return useD3(renderFn, dependencies);
}

export default useD3;