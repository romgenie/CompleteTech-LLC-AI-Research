import React from 'react';
import { IconButton, Tooltip } from '@mui/material';
import StarIcon from '@mui/icons-material/Star';
import StarBorderIcon from '@mui/icons-material/StarBorder';

interface FavoriteButtonProps {
  isFavorite: boolean;
  onToggle: () => void;
  size?: 'small' | 'medium' | 'large';
  tooltipPlacement?: 'top' | 'bottom' | 'left' | 'right';
}

/**
 * Button for toggling favorite status
 */
const FavoriteButton: React.FC<FavoriteButtonProps> = ({
  isFavorite,
  onToggle,
  size = 'medium',
  tooltipPlacement = 'top'
}) => {
  return (
    <Tooltip title={isFavorite ? "Remove from favorites" : "Add to favorites"} placement={tooltipPlacement}>
      <IconButton 
        onClick={onToggle} 
        size={size} 
        color={isFavorite ? "warning" : "default"}
        aria-label={isFavorite ? "Remove from favorites" : "Add to favorites"}
      >
        {isFavorite ? <StarIcon /> : <StarBorderIcon />}
      </IconButton>
    </Tooltip>
  );
};

export default FavoriteButton;