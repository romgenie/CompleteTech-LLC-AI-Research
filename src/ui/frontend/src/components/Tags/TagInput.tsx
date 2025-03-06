import React, { useState } from 'react';
import { Chip, TextField, Box, Button } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';

interface TagInputProps {
  onAddTag: (tag: string) => void;
  existingTags: string[];
}

const TagInput: React.FC<TagInputProps> = ({ onAddTag, existingTags }) => {
  const [inputValue, setInputValue] = useState('');
  
  const handleAddTag = () => {
    if (inputValue.trim() && !existingTags.includes(inputValue.trim())) {
      onAddTag(inputValue.trim());
      setInputValue('');
    }
  };

  return (
    <Box display="flex" alignItems="center" gap={1}>
      <TextField
        size="small"
        label="Add Tag"
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        onKeyPress={(e) => {
          if (e.key === 'Enter') {
            e.preventDefault();
            handleAddTag();
          }
        }}
      />
      <Button 
        size="small" 
        variant="outlined" 
        startIcon={<AddIcon />}
        onClick={handleAddTag}
      >
        Add
      </Button>
    </Box>
  );
};

export default TagInput;