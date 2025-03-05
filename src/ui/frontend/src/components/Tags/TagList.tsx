import React from 'react';
import { Chip, Box } from '@mui/material';

interface TagListProps {
  tags: string[];
  onDeleteTag?: (tag: string) => void;
  onClick?: (tag: string) => void;
}

const TagList: React.FC<TagListProps> = ({ tags, onDeleteTag, onClick }) => {
  if (!tags || tags.length === 0) return null;
  
  return (
    <Box display="flex" flexWrap="wrap" gap={1}>
      {tags.map((tag) => (
        <Chip
          key={tag}
          label={tag}
          onClick={onClick ? () => onClick(tag) : undefined}
          onDelete={onDeleteTag ? () => onDeleteTag(tag) : undefined}
          size="small"
        />
      ))}
    </Box>
  );
};

export default TagList;