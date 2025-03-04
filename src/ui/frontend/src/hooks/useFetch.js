import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

/**
 * Custom hook for handling API requests with loading, error states, and retry capability
 * 
 * @param {string} url - The API endpoint URL
 * @param {Object} options - Request options like method, headers, data
 * @param {boolean} immediate - Whether to fetch immediately when component mounts
 * @param {Function} mockDataFn - Function to generate mock data if API fails
 * @returns {Object} - { data, loading, error, refetch }
 */
function useFetch(url, options = {}, immediate = true, mockDataFn = null) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(immediate);
  const [error, setError] = useState(null);
  const [retryCount, setRetryCount] = useState(0);
  
  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios({
        url,
        ...options,
        headers: {
          ...options.headers,
          'Authorization': localStorage.getItem('token') 
            ? `Bearer ${localStorage.getItem('token')}` 
            : undefined
        }
      });
      
      setData(response.data);
      setLoading(false);
    } catch (err) {
      console.error(`Error fetching from ${url}:`, err);
      
      // Exponential backoff for retries (max 3 retries)
      if (retryCount < 3) {
        const delay = Math.pow(2, retryCount) * 1000; // 1s, 2s, 4s
        console.log(`Retrying in ${delay}ms...`);
        
        setTimeout(() => {
          setRetryCount(prev => prev + 1);
          fetchData();
        }, delay);
      } else {
        setError(err);
        setLoading(false);
        
        // Fall back to mock data if provided and API failed
        if (mockDataFn) {
          console.log('Falling back to mock data');
          setData(mockDataFn());
        }
      }
    }
  }, [url, options, retryCount, mockDataFn]);
  
  useEffect(() => {
    if (immediate) {
      fetchData();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [immediate]);
  
  const refetch = useCallback(() => {
    setRetryCount(0); // Reset retry count
    return fetchData();
  }, [fetchData]);
  
  return { data, loading, error, refetch };
}

export default useFetch;