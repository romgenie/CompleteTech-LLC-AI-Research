import React from 'react';
import { Box, Typography, Chip } from '@mui/material';

interface TagFilterProps {
  availableTags: string[];
  selectedTags: string[];
  onTagSelect: (tag: string) => void;
  onTagRemove: (tag: string) => void;
}

const TagFilter: React.FC<TagFilterProps> = ({ 
  availableTags, 
  selectedTags, 
  onTagSelect, 
  onTagRemove 
}) => {
  if (availableTags.length === 0) return null;
  
  return (
    <Box>
      <Typography variant="subtitle2" gutterBottom>Filter by Tags:</Typography>
      
      {selectedTags.length > 0 && (
        <Box display="flex" flexWrap="wrap" gap={1} mb={2}>
          {selectedTags.map(tag => (
            <Chip
              key={tag}
              label={tag}
              onDelete={() => onTagRemove(tag)}
              color="primary"
              size="small"
            />
          ))}
        </Box>
      )}
      
      <Box display="flex" flexWrap="wrap" gap={1}>
        {availableTags
          .filter(tag => !selectedTags.includes(tag))
          .map(tag => (
            <Chip
              key={tag}
              label={tag}
              onClick={() => onTagSelect(tag)}
              variant="outlined"
              size="small"
            />
          ))}
      </Box>
    </Box>
  );
};

export default TagFilter;