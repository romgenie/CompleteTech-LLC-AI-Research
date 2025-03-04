import { useRef, useEffect } from 'react';
import * as d3 from 'd3';

/**
 * Custom hook for integrating D3 visualizations with React
 * 
 * @param {Function} renderChartFn - Function that contains D3 code to render the visualization
 * @param {Array} dependencies - Array of dependencies to trigger re-rendering
 * @returns {React.MutableRefObject} - Ref to attach to the DOM element for the visualization
 */
function useD3(renderChartFn, dependencies = []) {
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

export default useD3;