import { useCallback } from 'react';
import useLocalStorage from './useLocalStorage';

/**
 * Hook for managing favorite research queries
 * @returns Methods for getting, adding, and removing favorites
 */
function useFavorites() {
  // Store favorites in localStorage
  const [favorites, setFavorites] = useLocalStorage('research_favorites', [] as string[]);

  /**
   * Add a query to favorites
   * @param id - Query ID to add
   */
  const addFavorite = useCallback((id: string) => {
    setFavorites((prev: string[]) => {
      if (prev.includes(id)) return prev;
      return [...prev, id];
    });
  }, [setFavorites]);

  /**
   * Remove a query from favorites
   * @param id - Query ID to remove
   */
  const removeFavorite = useCallback((id: string) => {
    setFavorites((prev: string[]) => prev.filter(favId => favId !== id));
  }, [setFavorites]);

  /**
   * Toggle favorite status
   * @param id - Query ID to toggle
   */
  const toggleFavorite = useCallback((id: string) => {
    setFavorites((prev: string[]) => {
      if (prev.includes(id)) {
        return prev.filter(favId => favId !== id);
      }
      return [...prev, id];
    });
  }, [setFavorites]);

  /**
   * Check if a query is favorited
   * @param id - Query ID to check
   * @returns True if favorited
   */
  const isFavorite = useCallback((id: string) => {
    return favorites.includes(id);
  }, [favorites]);

  return {
    favorites,
    addFavorite,
    removeFavorite,
    toggleFavorite,
    isFavorite
  };
}

export default useFavorites;